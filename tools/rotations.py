#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rotations.py -- Total (finite) Euler rotation poles for the seven major
continental plates, relative to the spin axis / mantle reference frame
(anchor plate 000), from the MERDITH2021 global plate motion model.

=============================================================================
MODEL
=============================================================================
Name    : MERDITH2021 (a.k.a. "Merdith et al. 2021 1000-0 Ma model")
Valid   : 0 - 1000 Ma  (this file tabulates the full 0 - 1000 Ma range)
Anchor  : plate 000. Every rotation below is a TOTAL RECONSTRUCTION ROTATION
          of the moving plate with respect to plate 000 at that age. The
          rotation chain of the underlying .rot file (e.g. 101 -> 714 -> 701
          -> 001 -> 000, 801 -> 802 -> 701 -> 001 -> 000, etc.) has ALREADY
          been composed for you by the GPlates reconstruction-tree engine, so
          `relative_to_plate_id` is 0 for every row and NO further composition
          is required. Just apply the pole directly to present-day geometry.

CITATION (cite this if you use the numbers)
-------------------------------------------
Merdith, A.S., Williams, S.E., Collins, A.S., Tetley, M.G., Mulder, J.A.,
Blades, M.L., Young, A., Armistead, S.E., Cannon, J., Zahirovic, S. and
Muller, R.D., 2021. Extending full-plate tectonic models into deep time:
Linking the Neoproterozoic and the Phanerozoic. Earth-Science Reviews, 214,
103477. https://doi.org/10.1016/j.earscirev.2020.103477

Model data release (the actual rotation files):
Merdith, A.S. et al. Zenodo. https://doi.org/10.5281/zenodo.10346399
(earlier v1.1b release: https://doi.org/10.5281/zenodo.4485738)

Please also acknowledge the service that served the numbers:
GPlates Web Service (EarthByte, University of Sydney),
Muller, R.D. et al., 2018, GPlates: Building a virtual Earth through deep
time. Geochemistry, Geophysics, Geosystems, 19, 2243-2261.

LICENCE
-------
Creative Commons Attribution 4.0 International (CC BY 4.0), as stated on the
Zenodo records for the Merdith et al. (2021) plate model
(https://zenodo.org/records/4485738 and https://zenodo.org/records/10346399).
You may reuse and redistribute these numbers, including commercially,
provided you give attribution as above.

=============================================================================
PROVENANCE -- EXACT URLs THE NUMBERS CAME FROM
=============================================================================
All rotations were retrieved as JSON from the GPlates Web Service endpoint

    https://gws.gplates.org/rotation/get_euler_pole_and_angle

documented at https://gwsdoc.gplates.org/rotation/euler-pole-and-angle
The endpoint returns, per age and plate id, the triple
    [pole_longitude, pole_latitude, angle]   (all degrees)
which is re-ordered to (pole_lat, pole_lon, angle) in the table below.

The twelve request URLs used, verbatim (each block of numbers came from the
URL listed beside it):

  0-300 Ma, 20 Myr step
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=0&end=310&step=20&pids=101,201&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=0&end=310&step=20&pids=301,501&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=0&end=310&step=20&pids=701,801&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=0&end=310&step=20&pids=802&model=MERDITH2021
  10-290 Ma, 20 Myr step (interleaved to give an overall 10 Myr step)
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=10&end=300&step=20&pids=101,201&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=10&end=300&step=20&pids=301,501&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=10&end=300&step=20&pids=701,801&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=10&end=300&step=20&pids=802&model=MERDITH2021
  350-1000 Ma, 50 Myr step
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=350&end=1010&step=50&pids=101,201&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=350&end=1010&step=50&pids=301,501&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=350&end=1010&step=50&pids=701,801&model=MERDITH2021
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?start=350&end=1010&step=50&pids=802&model=MERDITH2021

Model metadata (time range 0-1000 Ma, description, Zenodo DOI) came from
    https://repo.gplates.org/webdav/pmm/config/models.json
The underlying rotation file itself is
    1000_0_rotfile_Merdith_et_al.rot
mirrored at
    https://raw.githubusercontent.com/GPlates/gplates-web-service/master/django/GWS/data/deprecated/MODELS/MERDITH2021/1000_0_rotfile_Merdith_et_al.rot
(not used directly here -- it is several MB of text and would be truncated by
a markdown-converting fetcher; the web service was used instead because it
composes the rotation chain server-side.)

=============================================================================
VERIFICATION THAT WAS ACTUALLY PERFORMED
=============================================================================
The tabulated poles were not taken on trust. Four of them were applied
locally with pygplates 1.0 to a test point and compared against the
independent GPlates Web Service reconstruction endpoint
    https://gws.gplates.org/reconstruct/reconstruct_points/
All four agreed to the 4 decimal places the service prints:

  plate 701, 200 Ma, (18.42 E, 33.92 S)  -> (-0.8982, -49.6982)   match
  plate 101, 300 Ma, (74.00 W, 40.70 N)  -> (-10.2384,  -3.6467)  match
  plate 801, 100 Ma, (151.20 E, 33.87 S) -> (168.2702, -64.7154)  match
  plate 802, 500 Ma, (0.00 E, 80.00 S)   -> (159.6748, -29.7323)  match

This also confirms the anchor plate is 000 and the sign/axis convention is
the standard GPlates one (see USAGE below). The `self_test()` function at the
bottom re-runs these checks locally if pygplates is importable.

=============================================================================
USAGE
=============================================================================
The rotation reconstructs a present-day point to its palaeo-position:

    import pygplates, math
    lat_p, lon_p, ang = 0.0, -27.3, -26.13          # plate 701 at 200 Ma
    fr = pygplates.FiniteRotation(
             pygplates.PointOnSphere(lat_p, lon_p), math.radians(ang))
    palaeo = fr * pygplates.PointOnSphere(present_lat, present_lon)

Without pygplates, the same thing is a right-handed rotation of the unit
vector about the pole axis by `angle` (Rodrigues' formula); `rotate_point()`
below implements it in pure Python and is checked against pygplates in
`self_test()`.

For an age not in the table, do NOT linearly interpolate the (lat, lon, angle)
triples -- that is wrong on a sphere. Interpolate with a proper SLERP of the
corresponding quaternions/finite rotations (pygplates.FiniteRotation.interpolate),
or re-query the web service at the age you want.

=============================================================================
KNOWN LIMITATIONS -- READ BEFORE DRAWING CONCLUSIONS
=============================================================================
1. Time range. Valid 0-1000 Ma only. There is nothing here before 1000 Ma,
   and the model itself does not extend further back. (If you need >1000 Ma,
   the CAO2024 model on the same service covers 0-1800 Ma.)
2. Palaeomagnetic reference frame. MERDITH2021 is built on a palaeomagnetic
   reference frame, so ABSOLUTE LONGITUDE IS NOT CONSTRAINED -- the magnetic
   field is axially symmetric. Relative plate positions and palaeolatitudes
   are meaningful; absolute palaeolongitude before ~200 Ma is essentially a
   free parameter and should not be over-interpreted. (The MULLER2022 model
   is the same kinematics optimised into a mantle reference frame if you
   want plausible longitudes.)
3. Composite model. Per the official description, MERDITH2021 is "broadly
   based on a modified combination of MULLER2016 for the last 230 Ma, the
   MATTHEWS2016_pmag_ref model for 250-410 Ma and a newly constructed model
   for earlier times." Expect changes in character/uncertainty across those
   ~230 Ma and ~410 Ma joins.
4. Uncertainty grows with age. Cenozoic-Mesozoic rotations are constrained by
   seafloor magnetic anomalies and fracture zones; Palaeozoic and especially
   Precambrian rotations rest on sparse palaeomagnetic poles and geological
   correlation. Neoproterozoic positions are hypotheses, not measurements.
5. Rigid plates only. These are rigid-plate finite rotations. Continental
   deformation (stretched margins, orogenic shortening, e.g. the India-Asia
   collision zone, the Basin and Range, the Alpine-Himalayan belt) is not
   represented, so present-day coastlines rotated back in time will overlap
   and gap by hundreds of kilometres in deformed regions.
6. Only 7 plate IDs. Continents are not single plates. Rotating a whole
   continent polygon with one plate id is an approximation: e.g. much of
   Europe west of the Urals is 301 but Iberia (304), Adria, Anatolia,
   Arabia (503), Greenland (102), Florida (102x), Patagonia, India (501) vs
   Sri Lanka, and West Antarctica (801x/804) all have their own ids and move
   separately, especially before ~150 Ma. For pre-Pangaea times (>~330 Ma)
   assigning "Europe" to 301 and "Asia" to 301 is particularly crude --
   Siberia (401), Baltica (302), North China (601) and South China (602)
   were separate continents.
7. Angles are reported unwrapped and may exceed +/-180 degrees (e.g. plate
   301 at 950 Ma has angle -215.7). That is a legitimate finite rotation;
   do not "normalise" it into the range -180..180 without also being careful
   -- the resulting orientation is the same, but interpolation between
   samples is not.
8. Plate 802 is East Antarctica. West Antarctica (and the Antarctic
   Peninsula) rotate separately in this model.
"""

# (plate_id, age_ma, pole_lat_deg, pole_lon_deg, angle_deg, relative_to_plate_id)
# relative_to_plate_id is 0 for every row: these are TOTAL rotations w.r.t. the
# anchor plate 000, with the model's rotation chain already composed.
ROTATIONS = [
    # --- 101 ---
    (101, 0, 90.0, 0.0, 0.0, 0),
    (101, 10, 25.13028958, 91.79993795, 6.01264958, 0),
    (101, 20, 36.95101464, 82.68429324, 8.93726403, 0),
    (101, 30, 43.57117671, 84.63759301, 12.12139197, 0),
    (101, 40, 42.28897961, 97.40309425, 17.36738499, 0),
    (101, 50, 47.66045557, 102.92082314, 20.62279598, 0),
    (101, 60, 49.3746082, 110.92618877, 24.29216449, 0),
    (101, 70, 52.48100124, 119.08064388, 27.58494086, 0),
    (101, 80, 60.13293781, 116.5147844, 30.66847501, 0),
    (101, 90, 67.86707391, 117.14607872, 34.43982763, 0),
    (101, 100, 71.67125211, 119.56199818, 39.41180963, 0),
    (101, 110, 72.49112209, 121.99863685, 44.90347113, 0),
    (101, 120, 74.50933996, 115.96440103, 50.22433903, 0),
    (101, 130, 73.02232492, 108.12572187, 53.08760943, 0),
    (101, 140, 71.03226089, 105.07056357, 56.18152, 0),
    (101, 150, 68.44036113, 100.93465209, 59.08423954, 0),
    (101, 160, 72.3539196, 75.53492469, 62.5829436, 0),
    (101, 170, 72.77347436, 61.26461037, 65.74482426, 0),
    (101, 180, 71.69065709, 45.04764732, 67.75006587, 0),
    (101, 190, 69.49673506, 36.01617392, 69.87254666, 0),
    (101, 200, 67.37213822, 33.45697927, 71.75192723, 0),
    (101, 210, 65.14746014, 33.6419124, 72.20204246, 0),
    (101, 220, 64.1841416, 38.24831965, 72.05947945, 0),
    (101, 230, 62.25841033, 51.91740871, 71.35680752, 0),
    (101, 240, 60.58377129, 61.29249734, 71.21717377, 0),
    (101, 250, 59.5920792, 68.98406795, 70.26090086, 0),
    (101, 260, 57.04422329, 73.62206332, 70.61441111, 0),
    (101, 270, 56.25065045, 72.0035543, 70.77910764, 0),
    (101, 280, 53.2397739, 72.08061197, 71.45252868, 0),
    (101, 290, 49.24749528, 72.74341366, 72.59250881, 0),
    (101, 300, 47.69212054, 69.595269, 73.17883382, 0),
    (101, 350, 20.41563765, 55.23812173, 76.58541665, 0),
    (101, 400, 0.78747995, 39.51083036, 83.28180501, 0),
    (101, 450, -28.05509729, 35.24727943, 88.06087181, 0),
    (101, 500, -37.59, 33.8534, 112.3918, 0),
    (101, 550, 40.07312855, -161.28871166, -121.421422, 0),
    (101, 600, 32.20786388, -160.08685704, -137.04482901, 0),
    (101, 650, 40.40580315, -174.93307543, -155.90113766, 0),
    (101, 700, 44.58, 159.82, -180.4, 0),
    (101, 750, 47.4055, 152.8538, -182.2878, 0),
    (101, 800, 47.13664695, 144.47863176, -171.18733033, 0),
    (101, 850, 35.93050042, 156.42794696, -174.68202323, 0),
    (101, 900, 37.56589573, 166.27832925, -185.1412428, 0),
    (101, 950, 45.37498711, 176.55151903, -194.32280849, 0),
    (101, 1000, 44.46603212, 178.08158479, -181.47685271, 0),
    # --- 201 ---
    (201, 0, 90.0, 0.0, 0.0, 0),
    (201, 10, 34.00034617, 80.34733383, 5.19395749, 0),
    (201, 20, 48.69985064, 53.18620385, 8.2390267, 0),
    (201, 30, 56.03683123, 47.17674676, 11.62562299, 0),
    (201, 40, 57.3188435, 71.07085162, 15.746614, 0),
    (201, 50, 62.74266715, 73.99062171, 18.71770011, 0),
    (201, 60, 66.01935249, 84.76828575, 21.82455718, 0),
    (201, 70, 69.24446969, 99.80686337, 24.7410124, 0),
    (201, 80, 74.9401201, 90.94972435, 28.37371128, 0),
    (201, 90, 82.23475353, 83.04651718, 31.57769932, 0),
    (201, 100, 86.79799094, 88.59088325, 35.05090493, 0),
    (201, 110, 87.59477014, 143.56415416, 38.86887154, 0),
    (201, 120, 87.82277734, -175.32142579, 42.75197332, 0),
    (201, 130, 87.97644812, 141.63377519, 43.09413603, 0),
    (201, 140, 84.29109207, 132.10666596, 43.25472628, 0),
    (201, 150, 80.90780943, 124.41183998, 43.19736521, 0),
    (201, 160, 85.68370083, 56.31446361, 42.69146745, 0),
    (201, 170, 84.64429504, 23.54285014, 42.73608635, 0),
    (201, 180, 78.87305615, 1.02924088, 42.93354628, 0),
    (201, 190, 74.19639904, -0.30511495, 43.17240265, 0),
    (201, 200, 71.77224435, 3.92891389, 43.11227019, 0),
    (201, 210, 69.23916277, 11.2405787, 42.88915161, 0),
    (201, 220, 69.90226242, 21.58237128, 42.28488973, 0),
    (201, 230, 71.04743406, 54.11835214, 41.40595934, 0),
    (201, 240, 69.14626376, 77.51784011, 41.64452224, 0),
    (201, 250, 66.70517199, 94.37667183, 42.43307584, 0),
    (201, 260, 62.13423884, 101.0846055, 43.4329409, 0),
    (201, 270, 61.1371361, 97.73885506, 43.3534394, 0),
    (201, 280, 56.53320654, 96.26236483, 44.14771726, 0),
    (201, 290, 50.53271439, 95.69298092, 45.72529883, 0),
    (201, 300, 48.39033175, 90.43018584, 45.92091666, 0),
    (201, 350, 18.68903134, 71.99652351, 63.95872578, 0),
    (201, 400, 12.11435544, 60.0350415, 72.1317904, 0),
    (201, 450, 5.15693918, -122.24377511, -114.81420732, 0),
    (201, 500, 0.153458, 67.28999662, 98.28237484, 0),
    (201, 550, -1.42019155, 53.25187499, 104.35142121, 0),
    (201, 600, -14.86919585, -121.32284568, -136.32462372, 0),
    (201, 650, -4.73677081, -136.52537272, -135.47368025, 0),
    (201, 700, 8.74574225, -156.88972122, -134.13344953, 0),
    (201, 750, 14.38475757, -159.18221799, -135.93548213, 0),
    (201, 800, 21.05492257, -157.65677356, -126.02463825, 0),
    (201, 850, 5.55698069, -159.90718582, -116.86760542, 0),
    (201, 900, -0.67982943, -158.71977212, -132.44873986, 0),
    (201, 950, -0.35221511, -155.24996075, -155.17125414, 0),
    (201, 1000, -0.61961799, -149.68588265, -147.65598436, 0),
    # --- 301 ---
    (301, 0, 90.0, 0.0, 0.0, 0),
    (301, 10, 4.36068625, 85.39363147, 4.7904755, 0),
    (301, 20, 5.29335046, 71.87877215, 6.15923759, 0),
    (301, 30, 12.95251415, 72.60976521, 7.48407157, 0),
    (301, 40, 16.37692073, 88.62962359, 10.73226244, 0),
    (301, 50, 24.07784312, 88.89751214, 11.39172468, 0),
    (301, 60, 28.42837396, 91.58498231, 12.29843908, 0),
    (301, 70, 32.78367777, 103.15614138, 12.71696887, 0),
    (301, 80, 42.69969768, 95.80627275, 13.43889963, 0),
    (301, 90, 56.35823532, 90.62737339, 15.44921725, 0),
    (301, 100, 65.58615481, 90.14292753, 19.85498456, 0),
    (301, 110, 68.38261666, 96.44685911, 24.905645, 0),
    (301, 120, 69.91454878, 88.86953307, 30.15672448, 0),
    (301, 130, 66.31761584, 86.94514326, 32.93864918, 0),
    (301, 140, 63.28630211, 89.27473265, 35.84543635, 0),
    (301, 150, 59.24440042, 89.80850182, 38.75456558, 0),
    (301, 160, 60.93757172, 64.41934193, 42.94499563, 0),
    (301, 170, 60.28644441, 53.89646465, 46.4203852, 0),
    (301, 180, 57.7274039, 42.81875606, 49.10214668, 0),
    (301, 190, 54.73110796, 37.39442937, 51.80902946, 0),
    (301, 200, 52.26472509, 36.50856681, 53.98621382, 0),
    (301, 210, 49.63762379, 37.25433388, 55.02223569, 0),
    (301, 220, 48.62718608, 41.24248056, 54.86069566, 0),
    (301, 230, 46.88131333, 53.18732626, 53.71927566, 0),
    (301, 240, 45.47875166, 61.87686741, 53.25930592, 0),
    (301, 250, 44.66378639, 68.96009091, 51.92607231, 0),
    (301, 260, 41.98352138, 74.09013021, 52.4808264, 0),
    (301, 270, 40.88181528, 72.82178661, 52.99000095, 0),
    (301, 280, 37.34303235, 73.74232809, 54.43316205, 0),
    (301, 290, 32.86540367, 75.34720131, 56.59953588, 0),
    (301, 300, 30.95712162, 72.68387225, 57.96461944, 0),
    (301, 350, 2.05463782, 61.42403369, 72.71626669, 0),
    (301, 400, 14.69501499, -133.38703392, -88.70558912, 0),
    (301, 450, -39.30867464, 41.14113414, 103.78485064, 0),
    (301, 500, -45.30837162, 40.57560595, 130.28723217, 0),
    (301, 550, 45.9791666, -154.61831674, -141.00338211, 0),
    (301, 600, 37.71399784, -151.95035105, -154.50482923, 0),
    (301, 650, 43.4672411, -167.19188075, -176.14954158, 0),
    (301, 700, 44.66316991, 167.06903677, -202.12252668, 0),
    (301, 750, 46.92754058, 159.60664112, -204.49642214, 0),
    (301, 800, 46.49971446, 151.2974099, -193.29189804, 0),
    (301, 850, 36.03617728, 164.67836233, -194.6692619, 0),
    (301, 900, 37.78980045, 174.5992712, -205.31309643, 0),
    (301, 950, 46.00526386, -175.50517755, -215.73727232, 0),
    (301, 1000, 45.77832899, -174.13653317, -202.72248002, 0),
    # --- 501 ---
    (501, 0, 90.0, 0.0, 0.0, 0),
    (501, 10, 16.72553918, -38.22201239, -5.29070766, 0),
    (501, 20, 23.84225619, -32.27158092, -8.29160593, 0),
    (501, 30, 19.89132958, -2.50572716, -12.5634652, 0),
    (501, 40, 17.47193287, -3.30830323, -20.00563742, 0),
    (501, 50, 13.95028065, 0.99958125, -27.09732342, 0),
    (501, 60, 11.64453029, 2.01595483, -40.60320836, 0),
    (501, 70, 11.94006198, 1.32637969, -55.24394051, 0),
    (501, 80, 11.82038788, 5.62905829, -62.13099638, 0),
    (501, 90, 11.66562427, 11.43667099, -67.82525765, 0),
    (501, 100, 11.11280777, 16.39925438, -72.86168448, 0),
    (501, 110, 10.09328566, 16.5644901, -77.7718422, 0),
    (501, 120, 9.91920469, 16.51105435, -81.25733644, 0),
    (501, 130, 7.65809686, 19.28485634, -86.22592601, 0),
    (501, 140, 6.38792745, 21.8721772, -89.42638118, 0),
    (501, 150, 5.55696192, 22.87305715, -90.77236093, 0),
    (501, 160, 8.32347245, 25.54080783, -85.67913139, 0),
    (501, 170, 10.27314888, 27.09663892, -83.66928704, 0),
    (501, 180, 12.84282718, 28.29717444, -79.35507033, 0),
    (501, 190, 13.93711632, 28.0063397, -76.21391894, 0),
    (501, 200, 14.08813556, 27.02062488, -74.60037312, 0),
    (501, 210, 13.75502368, 25.2161006, -73.15602666, 0),
    (501, 220, 12.39946405, 23.63388259, -74.33251935, 0),
    (501, 230, 8.76984086, 20.64617395, -79.47543219, 0),
    (501, 240, 6.4008562, 19.12076993, -83.92032317, 0),
    (501, 250, 4.71674555, 18.53407364, -88.1886162, 0),
    (501, 260, 3.15309928, 17.02821476, -90.89240249, 0),
    (501, 270, 3.0581639, 16.28664892, -89.9940953, 0),
    (501, 280, 1.89501735, 14.06205759, -90.30988767, 0),
    (501, 290, 0.2476603, 11.1631939, -91.32353722, 0),
    (501, 300, 0.08988793, 9.48526059, -89.2755904, 0),
    (501, 350, 7.12030789, 165.16543739, 83.96077073, 0),
    (501, 400, 6.77682714, 153.67699853, 75.41537838, 0),
    (501, 450, 13.99480861, 120.29867952, 95.71341536, 0),
    (501, 500, 14.70805832, 136.99870251, 96.15694058, 0),
    (501, 550, 5.49997209, 128.24597648, 77.21288831, 0),
    (501, 600, 10.89234463, 126.14925128, 26.87916088, 0),
    (501, 650, -31.4203745, 64.51765626, 31.50603244, 0),
    (501, 700, -39.25950438, 44.75868293, 64.16095903, 0),
    (501, 750, 72.86503848, 167.86490069, -60.51025439, 0),
    (501, 800, -47.2303998, -25.2212347, 79.75222112, 0),
    (501, 850, -43.39698982, -17.0716718, 90.63799831, 0),
    (501, 900, -44.77310467, -9.69632442, 97.67078669, 0),
    (501, 950, 50.35613113, -175.13754107, -102.46368877, 0),
    (501, 1000, 57.08970521, -141.64894061, -108.61607023, 0),
    # --- 701 ---
    (701, 0, 90.0, 0.0, 0.0, 0),
    (701, 10, -0.0, -82.81, -5.31, 0),
    (701, 20, -0.0, -88.08, -6.71, 0),
    (701, 30, -0.0, -77.92, -8.54, 0),
    (701, 40, -0.0, -62.66, -13.73, 0),
    (701, 50, -0.0, -55.61, -15.27, 0),
    (701, 60, -0.0, -50.26, -16.83, 0),
    (701, 70, -0.0, -41.44, -18.91, 0),
    (701, 80, -0.0, -37.85, -19.77, 0),
    (701, 90, -0.0, -28.77, -20.74, 0),
    (701, 100, -0.0, -20.3, -23.92, 0),
    (701, 110, -0.0, -14.57, -28.74, 0),
    (701, 120, -0.0, -10.72, -32.69, 0),
    (701, 130, -0.0, -11.27, -35.79, 0),
    (701, 140, -0.0, -11.76, -39.3, 0),
    (701, 150, -0.0, -13.45, -41.89, 0),
    (701, 160, -0.0, -14.78, -35.73, 0),
    (701, 170, -0.0, -15.19, -33.63, 0),
    (701, 180, -0.0, -18.43, -29.21, 0),
    (701, 190, -0.0, -23.01, -26.56, 0),
    (701, 200, -0.0, -27.3, -26.13, 0),
    (701, 210, -0.0, -32.74, -26.82, 0),
    (701, 220, -0.0, -33.41, -29.53, 0),
    (701, 230, -0.0, -31.54, -37.21, 0),
    (701, 240, -0.0, -29.58, -42.82, 0),
    (701, 250, -0.0, -27.13, -47.36, 0),
    (701, 260, -0.0, -27.45, -51.43, 0),
    (701, 270, -0.0, -29.05, -51.36, 0),
    (701, 280, -0.0, -31.79, -53.97, 0),
    (701, 290, -0.0, -34.77, -57.94, 0),
    (701, 300, -0.0, -38.02, -57.87, 0),
    (701, 350, -0.0, -63.62, -78.48, 0),
    (701, 400, -0.0, -76.45, -82.08, 0),
    (701, 450, 0.0, 89.0, 126.0, 0),
    (701, 500, -0.0, -78.97, -114.0, 0),
    (701, 550, -2.6577862, 87.19662209, 102.31648737, 0),
    (701, 600, 11.852, 72.8397, 75.1631, 0),
    (701, 650, -5.10174787, 52.43176398, 91.5339016, 0),
    (701, 700, -16.7656, 37.6379, 116.7094, 0),
    (701, 750, 13.4168, -146.6944, -132.7918, 0),
    (701, 800, 21.18078367, -142.6895279, -101.77897102, 0),
    (701, 850, 33.0097, -135.5, -72.7623, 0),
    (701, 900, 18.82377137, -136.13434569, -74.17288279, 0),
    (701, 950, 6.75421431, -129.52974072, -83.93026583, 0),
    (701, 1000, -0.7614579, -115.13261235, -68.86865982, 0),
    # --- 801 ---
    (801, 0, 90.0, 0.0, 0.0, 0),
    (801, 10, 11.65431302, -5.26480329, -4.70556104, 0),
    (801, 20, 13.94806868, 13.27261329, -8.55705155, 0),
    (801, 30, 11.60178698, 21.35840827, -14.62636458, 0),
    (801, 40, 9.61648913, 14.32775896, -21.33002446, 0),
    (801, 50, 6.15620262, 19.21334636, -23.27422794, 0),
    (801, 60, 4.01590894, 22.10683263, -25.37933614, 0),
    (801, 70, 4.07837057, 23.46563542, -28.39673549, 0),
    (801, 80, 1.83673813, 30.33849529, -28.22905609, 0),
    (801, 90, 0.12150695, 40.02912651, -30.15838137, 0),
    (801, 100, 0.63299131, -134.84771384, 33.41714599, 0),
    (801, 110, 3.91557242, 49.85087737, -35.1579215, 0),
    (801, 120, 8.17857592, 55.78364841, -36.78536887, 0),
    (801, 130, 5.84710072, 58.92992303, -39.31417561, 0),
    (801, 140, 4.34357695, 59.38119717, -41.24357332, 0),
    (801, 150, 2.82063412, 59.24345565, -42.27112912, 0),
    (801, 160, 7.16461641, 69.11573041, -41.57237506, 0),
    (801, 170, 9.1751603, 74.06064638, -42.47889994, 0),
    (801, 180, 12.88970478, 81.11180702, -42.24889369, 0),
    (801, 190, 15.57531981, 84.84593296, -40.96877164, 0),
    (801, 200, 17.3232804, 85.90509192, -39.52954498, 0),
    (801, 210, 19.44081691, 85.87257745, -37.35351742, 0),
    (801, 220, 19.1735458, 81.9339695, -35.95289706, 0),
    (801, 230, 15.59040526, 69.25558356, -34.52330311, 0),
    (801, 240, 11.76158437, 60.20330251, -35.13767862, 0),
    (801, 250, 7.93771724, 53.90812368, -37.08162281, 0),
    (801, 260, 5.98067401, 47.87942259, -37.68756066, 0),
    (801, 270, 6.95768194, 47.14977482, -36.53396034, 0),
    (801, 280, 7.33924639, 41.71594572, -35.25675289, 0),
    (801, 290, 7.34986463, 33.66163138, -34.39085426, 0),
    (801, 300, 10.06613132, 31.1240947, -32.05810992, 0),
    (801, 350, 24.7048664, -36.76468294, -32.89556017, 0),
    (801, 400, 33.37720199, -66.2411967, -37.62731735, 0),
    (801, 450, 21.11224921, -85.08762295, -83.04168613, 0),
    (801, 500, 18.26075127, -69.6790417, -66.99735969, 0),
    (801, 550, -26.48038559, 98.87450314, 78.20287875, 0),
    (801, 600, -16.40018304, 92.19173084, 71.32034306, 0),
    (801, 650, -28.35469421, 56.87165513, 64.52425916, 0),
    (801, 700, -33.19268215, 39.59438897, 92.11207779, 0),
    (801, 750, 37.92714341, -166.02767618, -78.9301413, 0),
    (801, 800, 14.13588732, 159.81843824, -59.33793959, 0),
    (801, 850, -6.67136576, 148.65461911, -72.75283429, 0),
    (801, 900, -6.13778425, 154.52649474, -90.38371567, 0),
    (801, 950, 3.30493782, 164.74350105, -103.53403844, 0),
    (801, 1000, 5.53671916, 167.29549335, -91.04170111, 0),
    # --- 802 ---
    (802, 0, 90.0, 0.0, 0.0, 0),
    (802, 10, 2.2326067, 86.63109649, 4.22487161, 0),
    (802, 20, 4.71703616, 70.88947235, 4.97965876, 0),
    (802, 30, 9.142489, 73.69196619, 5.1065928, 0),
    (802, 40, 7.70856962, 99.21097858, 7.65225211, 0),
    (802, 50, 10.57152809, 104.39831417, 6.93247254, 0),
    (802, 60, 9.50476217, 119.58926057, 6.24108849, 0),
    (802, 70, 1.72457018, -36.19062425, -6.55565727, 0),
    (802, 80, 7.33782546, -25.64421995, -3.66037916, 0),
    (802, 90, 2.40433826, 70.678574, -3.04647848, 0),
    (802, 100, 1.15755149, 88.85477966, -6.58256059, 0),
    (802, 110, 11.75061342, 97.77082045, -10.17613602, 0),
    (802, 120, 15.41584698, 106.65399158, -14.43512169, 0),
    (802, 130, 6.75800283, 104.63613639, -16.76045963, 0),
    (802, 140, 2.89127529, 101.20480843, -17.87651641, 0),
    (802, 150, 0.41216456, -80.97810543, 18.13447556, 0),
    (802, 160, 3.25080301, 116.53880967, -22.75792501, 0),
    (802, 170, 4.2026662, 121.00329322, -26.15011442, 0),
    (802, 180, 6.75981431, 129.04416565, -30.10638048, 0),
    (802, 190, 8.93311774, 134.59407484, -31.52937195, 0),
    (802, 200, 10.74249542, 137.85133377, -31.40760232, 0),
    (802, 210, 13.29815271, 141.63337825, -30.44040184, 0),
    (802, 220, 14.7477869, 141.37067856, -27.81295867, 0),
    (802, 230, 17.81895619, 134.95348626, -20.60307553, 0),
    (802, 240, 19.85942368, 124.16096663, -15.84996091, 0),
    (802, 250, 18.66359982, 106.974249, -13.09014355, 0),
    (802, 260, 21.97596623, 90.23750942, -10.68216294, 0),
    (802, 270, 27.77008053, 93.91443336, -9.98668446, 0),
    (802, 280, 44.65527892, 82.43023189, -8.04065772, 0),
    (802, 290, 63.86842747, 26.95736012, -7.60514636, 0),
    (802, 300, 78.76885503, -28.74698356, -8.47486532, 0),
    (802, 350, 35.47343742, -93.88270645, -39.75561013, 0),
    (802, 400, 34.68811672, -108.51261799, -53.8066799, 0),
    (802, 450, 29.35067227, -101.35351805, -102.19096652, 0),
    (802, 500, 28.86226206, -91.85720872, -81.30306346, 0),
    (802, 550, -34.11151025, 79.27663028, 95.82714037, 0),
    (802, 600, -24.08204069, 75.35665804, 92.17271105, 0),
    (802, 650, -24.59911025, 45.60922914, 92.32457946, 0),
    (802, 700, -27.34462673, 32.18300535, 119.74551559, 0),
    (802, 750, 25.28378136, -166.23517983, -104.03033986, 0),
    (802, 800, 2.160812, 176.85630133, -79.64645125, 0),
    (802, 850, -16.63020579, 167.76128686, -87.56731405, 0),
    (802, 900, -16.48731856, 168.75021661, -106.71894655, 0),
    (802, 950, -7.27449247, 173.84889792, -123.81257765, 0),
    (802, 1000, -4.5907372, 177.36334179, -112.64677611, 0),]

PLATE_NAMES = {
    0:   "Anchor / spin axis (mantle reference frame)",
    101: "North America (Laurentia)",
    201: "South America (Amazonia/Rio de la Plata)",
    301: "Eurasia (Baltica + Siberia proxy; European plate)",
    501: "India (Indian craton)",
    701: "Africa (Nubia / West African + Congo cratons)",
    801: "Australia",
    802: "East Antarctica",
}

# Convenience mapping from the user's continent polygons to a plate id.
# NOTE: this is the crude 1-continent = 1-plate approximation; see limitation 6.
CONTINENT_TO_PLATE = {
    "Africa":        701,
    "Europe":        301,
    "Asia":          301,
    "North America": 101,
    "South America": 201,
    "Antarctica":    802,
    "Australia":     801,
    "India":         501,
}

MODEL_NAME = "MERDITH2021"
MODEL_MIN_AGE_MA = 0.0
MODEL_MAX_AGE_MA = 1000.0
ANCHOR_PLATE_ID = 0
LICENCE = "CC BY 4.0 (Creative Commons Attribution 4.0 International)"
CITATION = (
    "Merdith, A.S., Williams, S.E., Collins, A.S., Tetley, M.G., Mulder, J.A., "
    "Blades, M.L., Young, A., Armistead, S.E., Cannon, J., Zahirovic, S. and "
    "Muller, R.D., 2021. Extending full-plate tectonic models into deep time: "
    "Linking the Neoproterozoic and the Phanerozoic. Earth-Science Reviews, "
    "214, 103477. doi:10.1016/j.earscirev.2020.103477. "
    "Model data: doi:10.5281/zenodo.10346399 (CC BY 4.0). "
    "Numbers retrieved from the GPlates Web Service, "
    "https://gws.gplates.org/rotation/get_euler_pole_and_angle"
)
SOURCE_URL_TEMPLATE = (
    "https://gws.gplates.org/rotation/get_euler_pole_and_angle"
    "?start={start}&end={end}&step={step}&pids={pids}&model=MERDITH2021"
)


# --------------------------------------------------------------------------
# Lookups
# --------------------------------------------------------------------------
def rotations_for_plate(plate_id):
    """All (age_ma, pole_lat, pole_lon, angle_deg) for one plate, age-ordered."""
    return [(a, la, lo, an) for (p, a, la, lo, an, _r) in ROTATIONS if p == plate_id]


def get_rotation(plate_id, age_ma):
    """Exact table lookup -> (pole_lat, pole_lon, angle_deg). No interpolation."""
    for (p, a, la, lo, an, _r) in ROTATIONS:
        if p == plate_id and abs(a - age_ma) < 1e-9:
            return (la, lo, an)
    raise KeyError("no tabulated rotation for plate %r at %r Ma" % (plate_id, age_ma))


def rotate_point(pole_lat, pole_lon, angle_deg, lat, lon):
    """Pure-python Rodrigues rotation. Returns (lat, lon) in degrees.

    Same convention as pygplates: right-handed rotation of the point about the
    pole axis by +angle_deg.
    """
    import math
    d2r, r2d = math.pi / 180.0, 180.0 / math.pi
    def to_xyz(la, lo):
        la, lo = la * d2r, lo * d2r
        return (math.cos(la) * math.cos(lo),
                math.cos(la) * math.sin(lo),
                math.sin(la))
    k = to_xyz(pole_lat, pole_lon)
    v = to_xyz(lat, lon)
    th = angle_deg * d2r
    c, s = math.cos(th), math.sin(th)
    kdotv = sum(ki * vi for ki, vi in zip(k, v))
    kxv = (k[1] * v[2] - k[2] * v[1],
           k[2] * v[0] - k[0] * v[2],
           k[0] * v[1] - k[1] * v[0])
    r = tuple(v[i] * c + kxv[i] * s + k[i] * kdotv * (1.0 - c) for i in range(3))
    n = math.sqrt(sum(x * x for x in r))
    r = tuple(x / n for x in r)
    return (math.asin(max(-1.0, min(1.0, r[2]))) * r2d,
            math.atan2(r[1], r[0]) * r2d)


# --------------------------------------------------------------------------
# Sanity checks
# --------------------------------------------------------------------------
def check():
    """Assert basic structural sanity of the table. Raises AssertionError."""
    assert ROTATIONS, "ROTATIONS is empty"
    seen = set()
    per_plate_last_age = {}
    for row in ROTATIONS:
        assert len(row) == 6, "row must be a 6-tuple: %r" % (row,)
        pid, age, plat, plon, ang, rel = row
        assert isinstance(pid, int) and pid > 0, "bad plate id: %r" % (row,)
        assert pid in PLATE_NAMES, "plate id %d missing from PLATE_NAMES" % pid
        assert rel == ANCHOR_PLATE_ID, "row is not relative to anchor 000: %r" % (row,)
        assert age >= 0.0, "negative age: %r" % (row,)
        assert MODEL_MIN_AGE_MA <= age <= MODEL_MAX_AGE_MA, \
            "age outside model validity 0-1000 Ma: %r" % (row,)
        assert -90.0 <= plat <= 90.0, "pole latitude out of range: %r" % (row,)
        assert -180.0 <= plon <= 180.0, "pole longitude out of range: %r" % (row,)
        assert -360.0 <= ang <= 360.0, "angle out of range: %r" % (row,)
        key = (pid, age)
        assert key not in seen, "duplicate (plate, age): %r" % (key,)
        seen.add(key)
        prev = per_plate_last_age.get(pid)
        assert prev is None or age > prev, \
            "ages not strictly increasing for plate %d: %r after %r" % (pid, age, prev)
        per_plate_last_age[pid] = age

    # every plate must be pinned to the identity rotation at 0 Ma
    for pid in PLATE_NAMES:
        if pid == ANCHOR_PLATE_ID:
            continue
        plat, plon, ang = get_rotation(pid, 0.0)
        assert abs(ang) < 1e-9, "plate %d is not identity at 0 Ma: %r" % (pid, ang)

    # every plate must carry the same age set
    age_sets = {}
    for pid in PLATE_NAMES:
        if pid == ANCHOR_PLATE_ID:
            continue
        age_sets[pid] = tuple(a for (a, _, _, _) in rotations_for_plate(pid))
    first = next(iter(age_sets.values()))
    for pid, ages in age_sets.items():
        assert ages == first, "plate %d has a different age sampling" % pid

    # the ages the caller asked for must all be present
    required = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260,
                280, 300, 350, 400, 450, 500, 550, 600, 700, 800, 900, 1000]
    for a in required:
        assert float(a) in set(first), "requested age %d Ma is missing" % a

    # pure-python rotation must reproduce the verified reference reconstructions
    reference = [
        (701, 200.0,  18.42, -33.92,  -0.8982, -49.6982),
        (101, 300.0, -74.00,  40.70, -10.2384,  -3.6467),
        (801, 100.0, 151.20, -33.87, 168.2702, -64.7154),
        (802, 500.0,   0.00, -80.00, 159.6748, -29.7323),
    ]
    for pid, age, lon0, lat0, exp_lon, exp_lat in reference:
        plat, plon, ang = get_rotation(pid, age)
        la, lo = rotate_point(plat, plon, ang, lat0, lon0)
        assert abs(la - exp_lat) < 1e-3 and abs(lo - exp_lon) < 1e-3, \
            ("reconstruction mismatch for plate %d at %g Ma: got (%.4f, %.4f), "
             "expected (%.4f, %.4f)" % (pid, age, lo, la, exp_lon, exp_lat))
    return True


def self_test():
    """Optional cross-check of rotate_point() against pygplates, if available."""
    try:
        import pygplates
        import math
    except ImportError:
        return "pygplates not available - skipped"
    worst = 0.0
    for (pid, age, plat, plon, ang, _r) in ROTATIONS:
        fr = pygplates.FiniteRotation(pygplates.PointOnSphere(plat, plon),
                                      math.radians(ang))
        for (lat0, lon0) in ((-33.92, 18.42), (40.7, -74.0), (0.0, 100.0)):
            pg_lat, pg_lon = (fr * pygplates.PointOnSphere(lat0, lon0)).to_lat_lon()
            py_lat, py_lon = rotate_point(plat, plon, ang, lat0, lon0)
            dlon = abs(((pg_lon - py_lon) + 180.0) % 360.0 - 180.0)
            worst = max(worst, abs(pg_lat - py_lat), dlon)
    assert worst < 1e-6, "rotate_point disagrees with pygplates by %g deg" % worst
    return "pygplates agreement: max discrepancy %.2e deg over %d rotations" % (
        worst, len(ROTATIONS))


def main():
    plates = [p for p in PLATE_NAMES if p != ANCHOR_PLATE_ID]
    ages = sorted({a for (_p, a, _la, _lo, _an, _r) in ROTATIONS})
    print("=" * 72)
    print("Plate rotation model: %s" % MODEL_NAME)
    print("Valid: %.0f - %.0f Ma   Anchor plate: %03d   Licence: %s"
          % (MODEL_MIN_AGE_MA, MODEL_MAX_AGE_MA, ANCHOR_PLATE_ID, LICENCE))
    print("=" * 72)
    print("%d total rotations = %d plates x %d ages"
          % (len(ROTATIONS), len(plates), len(ages)))
    print("Ages (Ma): %s" % ", ".join("%g" % a for a in ages))
    print()
    print("Plates:")
    for pid in sorted(plates):
        rr = rotations_for_plate(pid)
        amax = max(abs(an) for (_a, _la, _lo, an) in rr)
        print("  %3d  %-48s %2d ages, |angle| <= %6.2f deg"
              % (pid, PLATE_NAMES[pid], len(rr), amax))
    print()
    print("Sample -- total rotation w.r.t. plate 000 (pole_lat, pole_lon, angle):")
    hdr = "  age(Ma) " + "".join("%26s" % ("%d %s" % (p, PLATE_NAMES[p].split()[0]))
                                 for p in (101, 701, 802))
    print(hdr)
    for a in (0.0, 100.0, 200.0, 300.0, 500.0, 750.0, 1000.0):
        row = "  %7.0f " % a
        for p in (101, 701, 802):
            la, lo, an = get_rotation(p, a)
            row += "%26s" % ("%8.2f %8.2f %8.2f" % (la, lo, an))
        print(row)
    print()
    check()
    print("check(): all structural + range + reconstruction assertions passed.")
    print("self_test(): %s" % self_test())
    print()
    print("Cite as:")
    for line in __import__("textwrap").wrap(CITATION, 72):
        print("  " + line)


if __name__ == "__main__":
    main()
