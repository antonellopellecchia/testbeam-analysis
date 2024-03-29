import os, sys, pathlib
import argparse

import uproot
import numpy as np
import pandas as pd
import awkward as ak
import scipy
from scipy.optimize import curve_fit

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.ROOT)

def f_efficiency(x, zero_eff, tau):
    return zero_eff / (1 + x*tau)
    #return zero_eff*(1 - x*tau)

def efficiency_fit(rate, efficiency, err_efficiency):
    p0 = [max(efficiency), 0]
    popt, pcov = curve_fit(f_efficiency, rate, efficiency, sigma=err_efficiency, p0=p0)
    perr = np.sqrt(np.diag(pcov))
    return popt, perr

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scandir", type=pathlib.Path, help="Scan input directory")
    parser.add_argument("runfile", type=pathlib.Path, help="Run list file")
    parser.add_argument("rates", type=pathlib.Path, help="Rate calibration file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Log level")
    args = parser.parse_args()
    
    scan_df = pd.read_csv(args.scandir / "runs.csv")
    runs_df = pd.read_csv(args.runfile)
    scan_df = scan_df.merge(runs_df, on="run", how="inner")
    print(scan_df)

    rate_df = pd.read_csv(args.rates)#[["chamber", "source_abs", "rate", "rate_error"]]
    rate_df = rate_df[rate_df.chamber==3][["source_abs", "rate", "rate_error"]]
    rate_df.rename(columns={"source_abs": "source"}, inplace=True)
    if args.verbose: print("Runs:\n", rate_df)

    scan_df = scan_df.merge(rate_df, on="source", how="inner")
    if args.verbose: print("Runs:\n", scan_df)

    scan_df_nocomp = scan_df[scan_df["compensation"]=="no"]
    scan_df_comp = scan_df[scan_df["compensation"]=="yes"]
    
    efficiency_fig, efficiency_ax = plt.figure(figsize=(12,9)), plt.axes()
    #rate_nocomp, rate_comp = 1/scan_df_nocomp["source"], 1/scan_df_comp["source"]
    rate_nocomp, rate_comp = scan_df_nocomp["rate"], scan_df_comp["rate"]
    err_rate_nocomp, err_rate_comp = scan_df_nocomp["rate_error"], scan_df_comp["rate_error"]
    eff_nocomp, eff_comp = scan_df_nocomp["stat_efficiency"], scan_df_comp["stat_efficiency"]
    err_eff_nocomp, err_eff_comp = scan_df_nocomp["err_stat_efficiency"], scan_df_comp["err_stat_efficiency"]

    rate_x = np.linspace(min(rate_nocomp), max(rate_nocomp), 100) 
    nocomp_pars, nocomp_errs = efficiency_fit(rate_nocomp, eff_nocomp, err_eff_nocomp)
    efficiency_ax.plot(rate_x, f_efficiency(rate_x, *nocomp_pars), "--", color="red")
    comp_pars, comp_errs = efficiency_fit(rate_comp, eff_comp, err_eff_comp)
    efficiency_ax.plot(rate_x, f_efficiency(rate_x, *comp_pars), "--", color="blue")

    tau_nocomp, err_tau_nocomp = nocomp_pars[1]*1e9, nocomp_errs[1]*1e9
    tau_comp, err_tau_comp = comp_pars[1]*1e9, comp_errs[1]*1e9
    e0_nocomp, err_e0_nocomp = nocomp_pars[0], nocomp_errs[0]
    e0_comp, err_e0_comp = comp_pars[0], comp_errs[0]
    print("No compensation tau {0:1.1f} ± {1:1.1f} ns, ε0 {2:1.3f} ± {3:1.3f}".format(tau_nocomp, err_tau_nocomp, e0_nocomp, err_e0_nocomp))
    print("Compensation tau {0:1.1f} ± {1:1.1f} ns, ε0 {2:1.3f} ± {3:1.3f}".format(tau_comp, err_tau_comp, e0_comp, err_e0_comp))

    true_tau = tau_comp/(1+tau_comp*1e-9*rate_comp.max())
    err_true_tau = ((err_tau_comp*1e-9)**2/(tau_comp*1e-9)**4 + err_rate_comp.max()**2)**0.5 * (tau_comp*1e-9)**2 * 1e9
    print("True tau {0:1.1f} ± {1:1.1f}".format(true_tau, err_true_tau))

    efficiency_ax.errorbar(
        rate_nocomp, eff_nocomp, err_eff_nocomp, fmt="o",
        label=f"No compensation - $\\tau$ = {tau_nocomp:1.1f} ± {err_tau_nocomp:1.1f} ns", color="red"
    )
    efficiency_ax.errorbar(
        rate_comp, eff_comp, err_eff_comp, fmt="o",
        label=f"Compensation - $\\tau$ = {tau_comp:1.1f} ± {err_tau_comp:1.1f} ns", color="blue"
    )

    efficiency_ax.set_xlabel("Measured background rate (kHz/strip)")
    efficiency_ax.set_ylabel("Efficiency")
    efficiency_ax.set_xscale("log")
    efficiency_ax.set_ylim(.8, 1.)
    efficiency_ax.legend()
    hep.cms.text("Muon Preliminary", ax=efficiency_ax)
    efficiency_ax.text(
        1., 1.,
        "ME0 GIF++ test beam",
        weight="bold",
        va="bottom", ha="right", size=30,
        transform=efficiency_ax.transAxes
    )
    efficiency_fig.savefig(args.scandir / "rate_capability.png")
    efficiency_fig.savefig(args.scandir / "rate_capability.pdf")

    resolution_fig, resolution_ax = plt.figure(figsize=(12,9)), plt.axes()
    resolution_ax.errorbar(rate_nocomp, abs(scan_df_nocomp["space_resolution"]), scan_df_nocomp["err_space_resolution"], fmt="o--", label="No compensation", color="red")
    resolution_ax.errorbar(rate_comp, abs(scan_df_comp["space_resolution"]), scan_df_comp["err_space_resolution"], fmt="o--", label="Compensation", color="blue")
    resolution_ax.set_xlabel("Measured background rate (kHz/strip)")
    resolution_ax.set_ylabel("Space resolution (µm)")
    resolution_ax.set_xscale("log")
    resolution_ax.legend()
    hep.cms.text("Muon Preliminary", ax=resolution_ax)
    resolution_fig.savefig(args.scandir / "space_resolution.png")
    resolution_fig.savefig(args.scandir / "space_resolution.pdf")

    cls_fig, cls_ax = plt.figure(figsize=(12,9)), plt.axes()
    cls_ax.errorbar(rate_nocomp, scan_df_nocomp["cls_muon"], scan_df_nocomp["err_cls_muon"], fmt="o--", label="Muons no compensation", color="red")
    cls_ax.errorbar(rate_comp, scan_df_comp["cls_muon"], scan_df_comp["err_cls_muon"], fmt="o--", label="Muons compensation", color="blue")
    cls_ax.errorbar(rate_nocomp , scan_df_nocomp["cls_bkg"], scan_df_nocomp["err_cls_bkg"], fmt="o--", label="Background no compensation", color="purple")
    cls_ax.errorbar(rate_comp, scan_df_comp["cls_bkg"], scan_df_comp["err_cls_bkg"], fmt="o--", label="Background compensation", color="green")
    cls_ax.set_xlabel("Measured background rate (kHz/strip)")
    cls_ax.set_ylabel("Average cluster size")
    cls_ax.set_xscale("log")
    hep.cms.text("Muon Preliminary", ax=cls_ax)
    cls_ax.text(
        1., 1.,
        "ME0 GIF++ test beam",
        weight="bold",
        va="bottom", ha="right", size=30,
        transform=cls_ax.transAxes
    )
    cls_ax.legend()
    hep.cms.text("Muon Preliminary", ax=cls_ax)
    cls_fig.savefig(args.scandir / "cluster_size.png")
    cls_fig.savefig(args.scandir / "cluster_size.pdf")

if __name__=='__main__': main()
