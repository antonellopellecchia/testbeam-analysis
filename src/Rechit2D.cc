#include <iostream>
#include <vector>
#include <math.h>

#include "Rechit.h"
#include "Rechit2D.h"
#include "Cluster.h"

// Rechit2D::Rechit2D(int chamber, Cluster clusterX, Cluster clusterY) {
//     fChamber = chamber;
//     fRechitX = Rechit(chamber, 0, clusterX);
//     fRechitY = Rechit(chamber, 1, clusterY);
// }

Rechit2D::Rechit2D(int chamber, Rechit rechitX, Rechit rechitY) {
    fChamber = chamber;
    fRechitX = rechitX;
    fRechitY = rechitY;
}

void Rechit2D::setGlobalPosition(double x, double y, double z) {
    fRechitX.setGlobalPosition(x, z);
    fRechitY.setGlobalPosition(y, z);
}

double Rechit2D::getLocalX() { return fRechitX.getCenter(); }
double Rechit2D::getLocalY() { return fRechitY.getCenter(); }
double Rechit2D::getErrorX() { return fRechitX.getError(); }
double Rechit2D::getErrorY() { return fRechitY.getError(); }
double Rechit2D::getClusterSizeX() { return fRechitX.getClusterSize(); }
double Rechit2D::getClusterSizeY() { return fRechitY.getClusterSize(); }
int Rechit2D::getChamber() { return fChamber;}