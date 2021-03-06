#ifndef DEF_DETECTORGEOMETRY
#define DEF_DETECTORGEOMETRY

#include "Rechit.h"

class DetectorGeometry {

    public:
        Rechit createRechit(Cluster cluster);
        void setPosition(double x, double y, double z) {
            fPosition[0] = x;
            fPosition[1] = y;
            fPosition[2] = z;
        }
        void setPosition(double x, double y, double z, double theta) {
            setPosition(x, y, z);
            fTheta = theta;
        }

        double getPositionX() { return fPosition[0]; }
        double getPositionY() { return fPosition[1]; }
        double getPositionZ() { return fPosition[2]; }
        double getTheta() { return fTheta; }
        double getOriginY() { return fOriginY; }

        double getNEta() { return fNumberPartitions; }
        double getEtaHeight() { return fEtaHeight; }
        
        //virtual ~DetectorGeometry();

        double fPosition[3];
        double fTheta;
        double fOriginY;

        int fNumberPartitions;
        double fEtaHeight;
};

#endif