# =======================================================
# =======================================================
# Filename: statmisc.py
# Purpose: Miscellaneous functions for time series
# and other statistical tests
# matplotlib in python
# Created: Nov 22 2017
# =======================================================
# =======================================================

"""Miscellaneous statistical functions for atmospheric analysis"""

import numpy as np
import scipy.stats as st

# Calculate two-tailed signficance levels using t-test
def siglev(x=None,y=None,xbar=None,ybar=None,xstd=None,ystd=None,nx=None,ny=None,pooled=False):
    """Conduct unpaired-two sample t-test and signficance levels. Either pass
    the samples directly or the means, standard deviations and number of observ-
    ations. 
    Inputs:
        x: [Optional] 1st set of samples
        y: [Optional] 2nd set of samples
        xbar: [Optional] Mean of 1st sample set
        ybar: [Optional] Mean of 2nd sample set
        xstd: [Optional] Standard Deviation of 1st sample set
        ystd: [Optional] Standard Deviation of 2nd sample set
        nx: [Optional] Number of samples in 1st sample set
        ny: [Optional] Number of samples in 2nd sample set
        pooled: [Optional]: If pooled variances to be used. True => Pooled variance 
        else separate variances. Defaults to False
    Either x or (xbar, xstd, nx) should be passed. Both cannot be passed together
    Same holds for y
    To use for one sample t-tests, set ybar = population mean, ystd = 0, ny = 1 and pooled = False
    Output: 
        clevm: Signficance level using two sample t-test in percentage
    """
    

    if x is not None:
        if xbar is not None or xstd is not None or nx is not None:
            raise SystemError('siglev: both x and xbar/xstd/nx cannot be passed together.')

        xbar = np.ma.mean(x);
        sx = np.ma.std(x);
        nx = np.size(x);
    else:
        if xbar is None or xstd is None or nx is None:
            raise SystemError('siglev: at least x or xbar, xstd, nx should be passed.')
        else:
            sx = xstd

    if y is not None:
        if ybar is not None or ystd is not None or ny is not None:
            raise SystemError('siglev: both y and ybar/ystd/ny cannot be passed together.')
        ybar = np.ma.mean(y);
        sy = np.ma.std(y);
        ny = np.size(y);
    else:
        if ybar is None or ystd is None or ny is None:
            raise SystemError('siglev: at least y or ybar,ystd,ny should be passed.')
        else:
            sy = ystd

    dof = nx + ny - 2;
    
    if(pooled):
        denom = ((nx-1)*sx**2 + (ny-1)*sy**2)/(nx+ny-2)*(nx+ny)/(nx*ny);
    else:
        denom = (sx**2/nx + sy**2/ny)
    tval = np.ma.abs(xbar-ybar)/np.sqrt(denom);
    clevm = st.t.cdf(tval,dof);
    clevm = (1 - clevm)*2;
    clevm = (1 - clevm)*100;
    return clevm


# Calculating confidence intervals using t-test
def cnfint(xstd,nx,clev=0.95,tail=1):
    """ Calculates confidence interval using t-test.
        xstd: numpy array of standard deviation of the ensemble.
        nx: numpy array of number of members of the ensemble.
        clev: the confidence interval (default 0.95 => 95%).
        tail: single of double-sided tail. (default 1).
        return value: the width of the interval (symmetric in both up and down directions) is returned."""

    if tail==1:
        cl=clev
    else:
        cl=1. - (1-clev)/2.0

    sdbar = xstd/np.sqrt(nx);
    tinv_val = st.t.ppf(cl,nx-1);
    diff = tinv_val*sdbar;

    return diff

# Full Autocorrelation
def autocorr(a,v):

    """ Performs autocorrelation using the np.correlate
    in 'full' mode. Normalization has been added for 
    keeping the values between -1,1
    Inputs:
        a: Vector a; a 1D array only
        v: Vector b: a 1D array to be autocorrelated with a
    Outputs:
        corr: 1D array of lead/lag autocorrelations starting with -n/2 (lag v), 
        n/2 (lead v)"""

    import numpy as np

    if(len(a.shape) > 1):
        raise ValueError("Only 1D objects expected for a")
    if(len(v.shape) > 1):
        raise ValueError("Only 1D objects expected for v")

    a = (a - a.mean())/(a.std() * len(a))
    v = (v - v.mean())/v.std()

    corr = np.correlate(a, v, mode = 'full')

    return corr


# Smooth a time series for a given window
def smooth_ts(ts, window):
    
    """smooth_ts to apply an averaging window over a time series
    ts: the time series to be smoothed (1D)    
    window: a size for the window
    """    
    
    import numpy as np
    
    if(len(ts.shape) > 1):
        raise ValueError("Expected 1D vector for ts")
    if(not isinstance(window, int)):
        raise ValueError("Integer Expected for window")
    
    n = len(ts)
    
    ns = n-window+1
    
    ts_smooth = np.empty(ns, np.float)

    # Smooth the time series for specified window size    
    i = 0
    while (i+window <= n):
        ts_smooth[i] = np.mean(ts[i:i+window])
        i+=1
        
    return ts_smooth


# Runnning correlation between time series
def run_corr(arr1, arr2, window_size):
    """Running correlation between 2 1D arrays for given window size
    Inputs:
        arr1: 1D array
        arr2: 1D array of same size as arr1
        window: size of the of the window for calculating running correlation
    """
    
    # Input error handling
    a1 = arr1.shape
    a2 = arr2.shape
    if(len(a1) > 1):
        raise ValueError("Expected only 1D arrays for arr1")
    if(len(a2) > 1):
        raise ValueError("Expected only 1D arrays for arr2")
    a1 = len(arr1)
    a2 = len(arr2)
    if(a1 != a2):
        raise ValueError("Array size mismatch. Pass similarly sized arrays")
    
    # Calculate running correlation
    corr_size = a1 - window_size + 1
    run_corr_arr = np.empty(corr_size, np.float32)
    
    i = 0
    while(i+window_size-1 < a1):
        i_start = i
        i_end = i+window_size-1
        corr = np.corrcoef(arr1[i_start:i_end], arr2[i_start:i_end])[0][1]
        run_corr_arr[i] = corr
        i+=1
        
    return run_corr_arr

def mann_kendall(data):
    
    """Calculate the Mann Kendall test for Trend in data
    Inputs:
        data - A one dimensional dataset ranked in the order it was collected (A time series)
    Outputs:
        tau_ - Kendall test statistic (Close to 1/-1, strong trend, 0 no trend)
        p_ - p-value associated with the test statistic
    """
    
    if len(data.shape) > 1:
        raise ValueError("Only 1D arrays expected %d array was passed" %len(data.shape))
    
    x = np.arange(len(data))
    
    tau_, p_ = st.kendalltau(x, data, nan_policy="raise")
    
    return tau_, p_
    

if(__name__ == "__main__"):
    print("Import module and run")