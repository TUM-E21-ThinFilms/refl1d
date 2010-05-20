import sys; sys.path.append('../..'); sys.path.append('../../dream')
from math import pi
from refl1d import *
Probe.view = 'log' # log, linear, fresnel, or Q**4

#from refl1d import ncnrdat
#import periodictable

# Compute slits from dT given in the staj file
slits = 0.02*(ncnrdata.XRay.d_s1 - ncnrdata.XRay.d_s2)
instrument = ncnrdata.XRay(dLoL=0.005, slits_at_Tlo=slits)
probe = instrument.load('e1085009.log')
probe.log10_to_linear()  # old data was start with log_10 (R) rather than R

# Values from staj
Pt = SLD(name='Pt', rho=86.431, irho=42.41/(2*1.54))
Ni80Fe20 = SLD(name="Ni80Fe20", rho=63.121, irho=8.24/(2*1.54))
Pt55Fe45 = SLD(name="Pt55Fe45", rho=93.842, irho=32.2/(2*1.54))
seed = SLD(name="seed", rho=110.404, irho=42.41/(2*1.54))
glass = SLD(name="glass", rho=15.086, irho=1.55/(2*1.54))


sample = (glass%(17.53/2.35)
          + seed/22.9417%(20.72/2.35) 
          + Pt55Fe45/146.576%(20.22/2.35)
          + Ni80Fe20/508.784%(29.93/2.35) 
          + Pt/31.8477%(25.18/2.35) 
          + air)

# Values from fit
if 1:
    sample[0].interface.value = 7.53
    sample[0].material.rho.value = 15.38
    sample[0].material.irho.value = 0.41
    sample[1].thickness.value = 19.6
    sample[1].interface.value = 9.19
    sample[1].material.rho.value = 109.38
    sample[1].material.irho.value = 11.47
    sample[2].thickness.value = 150.06
    sample[2].interface.value = 8.92
    sample[2].material.rho.value = 98.52
    sample[2].material.irho.value = 10.59
    sample[3].thickness.value = 514.27
    sample[3].interface.value = 12.45
    sample[3].material.rho.value = 61.93
    sample[3].material.irho.value = 3.29
    sample[4].thickness.value = 25.01
    sample[4].interface.value = 10.89
    sample[4].material.rho.value = 92.02
    sample[4].material.irho.value = 11.93

# Fit parameters
#probe.theta_offset.dev(radians(0.01)/sqrt(12))  # accurate to 0.01 degrees

if 0: # Open set
    for i,L in enumerate(sample[0:-1]):
        if i>0: L.thickness.range(0,1000)
        L.interface.range(0,50)
        L.material.rho.range(0,200)
        L.material.irho.range(0,200)
elif 0: # jiggle
    for i,L in enumerate(sample[0:-1]):
        if i>0: L.thickness.pmp(0,10)
        L.interface.pmp(0,10)
        L.material.rho.pmp(10)
        L.material.irho.pmp(10)
elif 0: # grower
    sample[1].thickness.value = 25
    sample[2].thickness.value = 200
    sample[3].thickness.value = 500
    sample[4].thickness.value = 25
    for i,L in enumerate(sample[0:-1]):
        L.interface.value = 20
        L.material.rho.value = 0.5*int(2*L.material.rho.value)
        L.material.irho.value = 0.5*int(2*L.material.rho.value)
        if i > 0: L.thickness.pmp(-50,100)
        L.interface.pmp(100)
        L.material.rho.pmp(10)
        L.material.irho.pmp(10)
    
elif 1: # d2 X d3
    #sample[2].thickness.range(0,400)
    #sample[3].thickness.range(0,1000)
    sample[2].thickness.range(50,400)
    sample[3].thickness.range(50,1000)
    sample[2].thickness.value = 400
    sample[3].thickness.value = 1000

M = Experiment(probe=probe, sample=sample)

from refl1d.mystic.parameter import randomize, varying
randomize(varying(M.parameters()))

# Do the fit
if 0:
    result = preview(models=M)
elif 0:
    result = fit(models=[M], npop=10)
    result.show()
elif 0:
    import dream
    mc = dream.load_state('grower2')
    mc.show(portion=1)
elif 0:
    result = fit(models=M).show()
elif 0:
    from dream.corrplot import COLORMAP
    import pylab
    from numpy import min,exp
    x,y,image = mesh(models=M, 
                 vars=[sample[2].thickness,sample[3].thickness],
                 n=200)
    vmax = 100*min(image)
    image[image>vmax] = vmax 
    pylab.pcolormesh(y,x,-0.5*image.T, cmap=COLORMAP)
    pylab.colorbar()
    pylab.show()
else:
    mc = draw_samples(models=M, chains=10, generations=500)
    # full is 10n pop using full range 1x1500 gen
    # full2 is 10n pop using full range repeated, but with randomized initial
    # grower is 10n pop over 3*1000 gen using nominal grower values
    # grower2 is 20n pop over 5*2000 gen using nominal grower values
    mc.save('d1xd2-fit')
    mc.show(portion=0.5)
    
