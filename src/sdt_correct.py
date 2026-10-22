"""Hautus (1995) / Stanislaw & Todorov (1999) log-linear SDT correction, as promised in 5.2.
Add 0.5 to hit & false-alarm counts and 1.0 to signal & noise trial totals before proportions;
d' = z(H) - z(F), c = -0.5*(z(H)+z(F)). The shipped .xlsx stores already-corrected d'/c;
this module documents + tests the upstream rule so the method exists in code, not only prose."""
import numpy as np
from scipy.stats import norm
def sdt(hit, fa, n_signal, n_noise):
    H=(hit+0.5)/(n_signal+1.0); F=(fa+0.5)/(n_noise+1.0)
    zH,zF=norm.ppf(H),norm.ppf(F)
    return dict(dprime=zH-zF, criterion_c=-0.5*(zH+zF), H=H, F=F)
if __name__=="__main__":
    out=sdt(hit=50, fa=0, n_signal=50, n_noise=50)
    assert np.isfinite(out["dprime"]) and np.isfinite(out["criterion_c"])
    print("[sdt] edge case finite:", {k:round(v,4) for k,v in out.items()})
