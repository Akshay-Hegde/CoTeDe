*************************
Tests for Quality Control
*************************

These are the tests available, and can be explicity accessed at cotede.qctests. 
Most of them simply reproduce the procedure recommended by GTSPP, EuroGOOS, IMOS, ARGO and others.

Although I slightly modified the names of some Q.C. test, the concept behind is still the same. 
The goal was to normalize all tests to return True if the data is good and False if the data is bad. 
For example, ARGO's manual define "Impossible Date Test", while here I call it "`Valid Date`_". 


The result of each test for each measurement is coded according to recommendation of IOC given in the table below. 
For example, if the climatology database is not available, the output flag would be 0, while a fail on the same climatology test would return a flag 3 for GTSPP procedure.

Flag table

====    =======
Flag    Meaning
====    =======
0       No QC was performed
1       Good data
2       Probably good data
3       Probably bad data
4       Bad data
9       Missing data
====    =======


=====
Tests
=====

Valid Date
~~~~~~~~~~

Check if there is a valid date and time associated with the measurement.

Valid Position
~~~~~~~~~~~~~~

Check if there is a valid position associated with the measuremnt. It should have a latitude between -90 and 90, and a longitude between -180 and 360.

Location at Sea
~~~~~~~~~~~~~~~

Check if the position is at sea, which is evaluated using ETOPO1, a bathymetry with resolution of 1 minute.
It is considered at sea if the interpolated position has a negative vertical level.

This test implicitly requires to be approved by the `Valid Position`_ test.

Global Range
~~~~~~~~~~~~

This test evaluates if the measurement is a possible value in the ocean in normal conditions. 
The thresholds used are extreme values, wide enough to accommodate all possible values and do not discard uncommon, but possible, conditions.

Regional Range
~~~~~~~~~~~~~~

Digit Rollover
~~~~~~~~~~~~~~~

Every sensor has a limit of bits available to store the sample value, with this limit planned to cover the possible range.
A spurious value over the bit range would be recorded as the scale rollover, resulting in a misleading value inside the possible scale.
This test identifies extreme jumps on consecutive measurements, that area wider than expected, suggesting a rollover error.

The difference on consecutive measurements must be smaller or equal to the threshold to be approved.

Gradient
~~~~~~~~

  This test compares

    .. math::

       X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right|

Spike
~~~~~

.. math::

   X_i = \left| V_i - \frac{V_{i+1} + V_{i-1}}{2} \right| - \left| \frac{V_{i+1} - V_{i-1}}{2} \right|

Tukey 53H
~~~~~~~~~

This method to detect spikes is based on the procedure initially proposed by \citet{GoringNikora2002} for Acoustic Doppler Velocimeters, and similar to the one adopted by \citet{Morello2011}.
It takes advantage of the robustness of the median to create a smoother data series, which is then compared with the observation.
This difference is normalized by the standard deviation of the observed data series after removing the large--scale variability.

For one individual measurement :math:`x_i`, where :math:`i` is the position of the observation, it is evaluated as follows:

1. :math:`x^{(1)}` is the median of the five points from :math:`x_{i-2}` to :math:`x_{i+2}`;
2. :math:`x^{(2)}` is the median of the three points from :math:`x^{(1)}_{i-1}` to :math:`x^{(1)}_{i+1}`;
3. :math:`x^{(3)}` is the defined by the Hanning smoothing filter:
        :math:`\frac{1}{4}\left( x^{(2)}_{i-1} +2x^{(2)}_{i} +x^{(2)}_{i+1} \right)`
4. :math:`x_i` is a spike if :math:`\frac{|x_i-x^{(3)}|}{\sigma} > k`, where :math:`\sigma` is the standard deviation of the lowpass filtered data.


The default behavior in CoTeDe is to flag 4 if the test yields values higher than :math:`k=1.5`, and flag 1 if it is lower.


Climatology
~~~~~~~~~~~

.. math::

    X_i = \frac{V_{it} - <V_t>}{\sigma}


=========================
Quality Control procedure
=========================



CTD
~~~

GTSPP

+--------------------+------------+--------+-------------+----------+
| Test               |         Flag        |       Threshold        |
+--------------------+------------+--------+-------------+----------+
|                    | if succeed | if fail| Temperature | Salinity |
+====================+============+========+=============+==========+
|                    |            |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Date`_      |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Position`_  |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Location at Sea`_ |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Global Range`_    |  1         |        | -2 to 40 C  | 0 to 41  |
+--------------------+------------+--------+-------------+----------+
| `Gradient`_        |  1         | 4      | 10.0 C      | 5        |
+--------------------+------------+--------+-------------+----------+
| `Spike`_           |  1         |        | 2.0 C       | 0.3      |
+--------------------+------------+--------+-------------+----------+
| `Climatology`_     |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+
| `Profile Envelop`_ |            |        |                        |
+--------------------+------------+--------+-------------+----------+


EuroGOOS

+--------------------+------------+--------+-------------+----------+
| Test               |         Flag        |       Threshold        |
+--------------------+------------+--------+-------------+----------+
|                    | if succeed | if fail| Temperature | Salinity |
+====================+============+========+=============+==========+
| `Valid Date`_      |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Position`_  |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Location at Sea`_ |  1         | 4      |                        |
+--------------------+------------+--------+-------------+----------+
| `Global Range`_    |  1         | 4      | -2.5 to 40  | 2 to 41  |
+--------------------+------------+--------+-------------+----------+
| `Digit Rollover`_  |  1         | 4      |  10.0 C     | 5        |
+--------------------+------------+--------+-------------+----------+
| Gradient Cond.     |  1         | 4      |             |          |
|  - < 500           |            |        | 9.0 C       | 1.5      |
|  - > 500           |            |        | 3.0 C       | 0.5      |
+--------------------+------------+--------+-------------+----------+
| Spike Cond.        |  1         | 4      |             |          |
+--------------------+------------+--------+-------------+----------+
| `Climatology`_     |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+


IMOS (Incomplete)

+--------------------+------------+--------+-------------+----------+
| Test               |         Flag        |       Threshold        |
+--------------------+------------+--------+-------------+----------+
|                    | if succeed | if fail| Temperature | Salinity |
+====================+============+========+=============+==========+
| `Valid Date`_      |  1         | 3      |                        |
+--------------------+------------+--------+-------------+----------+
| `Valid Position`_  |  1         | 3      |                        |
+--------------------+------------+--------+-------------+----------+
| `Location at Sea`_ |  1         | 3      |                        |
+--------------------+------------+--------+-------------+----------+
| `Global Range`_    |  1         |        | -2.5 to 40  | 2 to 41  |
+--------------------+------------+--------+-------------+----------+
| `Gradient`_        |  1         | 4      | 10.0 C      | 5        |
+--------------------+------------+--------+-------------+----------+
| `Spike`_           |  1         |        | 2.0 C       | 0.3      |
+--------------------+------------+--------+-------------+----------+
| `Climatology`_     |  1         |        |                        |
+--------------------+------------+--------+-------------+----------+


TSG
~~~

Based on AOML procedure. Realtime data is evaluatd by tests 1 to 10, while the delayed mode is evaluated by tests 1 to 15.

  1. Platform Identification
  2. `Valid Date`_
  3. Impossible Location
  4. `Location at Sea`_
  5. Impossible Speed
  6. `Global Range`_
  7. Regional Ranges
  8. `Spike`_
  9. Constant Value
  10. `Gradient`_
  11. Climatology
..  12. NCEP Weekly analysis
..  13. Buddy Check
..  14. Water Samples
..  15. Calibrations

XBT
~~~

ARGO
~~~~

  1. Platform Identification
  2. `Valid Date`_  For ARGO, the year also must be later than 1997.
  3. Impossible location test
  4. Position on land test
  5. Impossible speed test
  6. `Global range`_
  7. Regional range test
  8. Pressure increasing test
  9. `Spike`_
  10. Top an dbottom spike test: obsolete
  11. `Gradient`_
  12. `Digit Rollover`_
  13. Stuck value test
  14. Density inversion
  15. Grey list
  16. Gross salinity or temperature sensor drift
  17. Visual QC
  18. Frozen profile test
  19. Deepest pressure test


==========
References
==========
