"""
Fit a linear or logistic curve to a series of points.

Sahil Shah
Alex Hofmann
Roy Hyunjin Han
"""


# Import system modules
import scipy.stats
import numpy
import math
import copy


class Curve(object):

    'Abstract class for fitting curves to points'

    def __init__(self, xs, ys):
        # Set
        self.xs = xs
        self.ys = ys
        # Fit
        self.fit(copy.copy(xs), copy.copy(ys))

    def fit(self, xs, ys):
        'Fit a curve using the given coordinates'
        pass

    def interpolate(self, x):
        'Interpolate the identity function'
        return x

    def plot(self, targetPath=None, xLabel='', yLabel='', title='', dpi=500):
        'Plot the curve'
        # Prepare
        minimumX, maximumX = min(self.xs), max(self.xs)
        meshXs = numpy.arange(minimumX - 500, maximumX + 500, 0.5)
        import pylab
        pylab.cla()
        # Plot
        pylab.plot(self.xs, self.ys, 'ro')
        pylab.plot(meshXs, self.interpolate(meshXs))
        # Annotate
        leftX, bottomY, rightX, topY = pylab.axis()
        width, height = rightX - leftX, topY - bottomY
        pylab.text(0.25 * width + leftX, 0.75 * height + bottomY, 'r-squared = %s' % pow(self.rValue, 2))
        pylab.xlabel(xLabel)
        pylab.ylabel(yLabel)
        pylab.title(title)
        # Show

        if targetPath:
            pylab.savefig(targetPath, dpi=dpi)
        else:
            pylab.show()


class LinearCurve(Curve):

    def fit(self, xs, ys):
        self.gradient, self.intercept, self.rValue, pValue, standardError = scipy.stats.linregress(xs, ys)

    def interpolate(self, x):
        return self.gradient * x + self.intercept


class LogisticCurve(Curve):

    ASYMPTOTE_OFFSET = 0.01
    FAKE_COUNT = 10
    FAKE_INTERVAL = 100

    def fit(self, xs, ys):
        # Prepare
        minimumY, maximumY = min(ys), max(ys)
        minimumX, maximumX = min(xs), max(xs)
        # Record as floats to prevent integer rounding during division
        self.upperBound = float(maximumY + self.ASYMPTOTE_OFFSET)
        self.lowerBound = float(minimumY - self.ASYMPTOTE_OFFSET)
        # If there are too few points,
        if len(xs) < 3:
            # Add more points on the right
            xs.extend(maximumX + self.FAKE_INTERVAL * (i + 1) for i in xrange(self.FAKE_COUNT))
            ys.extend([maximumY] * self.FAKE_COUNT)
            # Add more points on the left
            xs.extend(minimumX - self.FAKE_INTERVAL * (i + 1) for i in xrange(self.FAKE_COUNT))
            ys.extend([minimumY] * self.FAKE_COUNT)
            # Sort
            xs.sort()
            ys.sort()
        # Transform points using a linearization of the logistic function
        transformedYs = [math.log(((self.upperBound / y) - 1) / (1 - (self.lowerBound / y))) for y in ys]
        # Fit a line to the transformed points
        gradient, intercept, self.rValue, pValue, standardError = scipy.stats.linregress(xs, transformedYs)
        # Find the logistic function
        self.baseFactor = math.exp(intercept)
        self.exponentFactor = gradient

    def interpolate(self, x):
        height = self.upperBound - self.lowerBound
        return self.lowerBound + (height / (1 + self.baseFactor * numpy.exp(self.exponentFactor * x)))

from StringIO import StringIO
def get_curve(x, y, interpolate, dpi,
              xLabel=None, yLabel=None, title=None, type=LogisticCurve):
    curve = type(x,y)
    curve.interpolate(interpolate)
    
    fp = StringIO()
    curve.plot(targetPath=fp, xLabel=xLabel, yLabel=yLabel, title=title, dpi=dpi)
    
    fp.seek(0)
    bin = fp.read()
    fp.close()

    return bin
