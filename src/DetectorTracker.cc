#include <math.h>

#include "Cluster.h"
#include "Rechit.h"
#include "Rechit2D.h"
#include "DetectorTracker.h"

DetectorTracker::DetectorTracker(int oh, int chamber, double sizeX, double sizeY, int nStrips) {
    fOh = oh;
    fChamber = chamber;
    fSize[0] = sizeX;
    fSize[1] = sizeY;
    fNumberStrips = nStrips;
    fStripPitch = sizeX / fNumberStrips;
    fStripPitchSqrt12 = fStripPitch * 0.288675;
}

Rechit DetectorTracker::createRechit(Cluster cluster) {
    return Rechit(
        fChamber,
        fScale[cluster.getDirection()]*(-0.5*fSize[cluster.getDirection()] + fStripPitch*cluster.getCenter()),
        cluster.getSize() * fStripPitchSqrt12,
        cluster.getSize()
    );
}

Rechit2D DetectorTracker::createRechit2D(Cluster cluster1, Cluster cluster2) {
    return Rechit2D(fChamber, createRechit(cluster1), createRechit(cluster2));
}

void DetectorTracker::mapRechit2D(Rechit2D *rechit) {
    // map already existing rechit to global detector geometry
    double globalX = rechit->getLocalX() - fPosition[0];
    double globalY = rechit->getLocalY() - fPosition[1];
    rechit->setGlobalPosition(
        globalX*cos(fTheta) - globalY*sin(fTheta),
        globalX*sin(fTheta) + globalY*cos(fTheta),
        fPosition[2]
    );
}