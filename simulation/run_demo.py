import time
import numpy as np
from simulation.config import SEED
from simulation import data_generator, dwell_decomposition, for_validator
from simulation import gaming_detector, trust_engine, kitchenpulse_score
from simulation import evaluate, label_noise_experiment, dispatch_simulator
from simulation import explainability, scenario_simulator, visualize


def main():
    start = time.time()

    print("=" * 60)
    print("  🚀 KitchenPulse Simulation — Team Escape")
    print("=" * 60)

    rng = np.random.default_rng(SEED)

    print("\n📊 STEP 1: Data Generation")
    merchants, orders = data_generator.run(SEED)

    print("\n🔧 STEP 2: Signal Processing")
    corrected_dwell = dwell_decomposition.run(orders, merchants)
    orders["corrected_dwell"] = corrected_dwell.values

    for_flags, for_scores = for_validator.run(orders)
    orders["for_flag"] = for_flags.values

    gaming_results = gaming_detector.run(orders, for_scores)

    print("\n🧠 STEP 3: Trust Engine")
    trust_profiles = trust_engine.run(orders, merchants, corrected_dwell, for_scores, gaming_results)

    print("\n🧮 STEP 4: Model Evaluation")
    model_results = evaluate.run_all_models(orders, trust_profiles, merchants, SEED, for_scores=for_scores)

    print("\n🔬 STEP 5: Label Noise Experiment")
    noise_results = label_noise_experiment.run(orders)

    print("\n🚚 STEP 6: Dispatch Simulation")
    orders["pred_baseline"] = model_results["Baseline"]["predictions"]
    orders["pred_dwell"] = model_results["Dwell-Corrected"]["predictions"]
    orders["pred_kplite"] = model_results["KP-Lite"]["predictions"]
    orders["pred_kpfull"] = model_results["KP-Full"]["predictions"]
    dispatch_results = dispatch_simulator.run(
        orders,
        {
            "Baseline": "pred_baseline",
            "Dwell-Corrected": "pred_dwell",
            "KP-Lite": "pred_kplite",
            "KP-Full": "pred_kpfull",
        },
        SEED,
    )

    print("\n🎯 STEP 7: Scenario Simulator")
    scenario_results = scenario_simulator.run()

    print("\n💡 STEP 8: Explainability (Sample)")
    sample_explanations = explainability.explain_batch(orders, trust_profiles, merchants, n_samples=5)
    for expl in sample_explanations[:3]:
        print(f"    Pred={expl['prediction']}min, True={expl['true_kpt']}min, Error={expl['error']}min")
        for b in expl["breakdown"]:
            print(f"      {b['signal']:>10s}: w={b['weight']:.2f} × {b['estimate_min']:.0f}min = {b['contribution_min']:.1f}min")

    print("\n📈 STEP 9: Generating Charts")
    visualize.generate_all_charts(model_results, orders, trust_profiles, noise_results, dispatch_results)

    print("\n🌐 STEP 10: Exporting Dashboard Data")
    visualize.export_dashboard_json(
        model_results, orders, trust_profiles, noise_results,
        dispatch_results, scenario_results, for_scores,
    )
    print("  Dashboard data exported to dashboard/data/")

    elapsed = time.time() - start

    print("\n" + "=" * 60)
    bl = model_results["Baseline"]["metrics"]
    kf = model_results["KP-Full"]["metrics"]
    mae_drop = (1 - kf["mae"] / bl["mae"]) * 100
    p90_drop = (1 - kf["p90_error"] / bl["p90_error"]) * 100
    print(f"  🏆 RESULTS SUMMARY")
    print(f"  {'Metric':<25s} {'Baseline':>10s} {'KP-Full':>10s} {'Change':>10s}")
    print(f"  {'-'*55}")
    print(f"  {'MAE (min)':<25s} {bl['mae']:>10.1f} {kf['mae']:>10.1f} {'↓'+str(round(mae_drop))+'%':>10s}")
    print(f"  {'P90 Error (min)':<25s} {bl['p90_error']:>10.1f} {kf['p90_error']:>10.1f} {'↓'+str(round(p90_drop))+'%':>10s}")
    print(f"  {'Within ±3min':<25s} {bl['within_3min']*100:>9.0f}% {kf['within_3min']*100:>9.0f}%")
    print(f"  {'ETA Volatility':<25s} {bl.get('avg_eta_volatility',0):>10.2f} {kf.get('avg_eta_volatility',0):>10.2f}")
    print(f"  {'-'*55}")
    print(f"  ⏱️  Completed in {elapsed:.1f} seconds")
    print(f"  ✅ Open dashboard/index.html to view interactive results")
    print("=" * 60)


if __name__ == "__main__":
    main()
