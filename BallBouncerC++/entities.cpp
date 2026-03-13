#include <cmath>
#include <stdio.h>
#include "common.h"

// Point definitions
Point::Point() {}
Point::Point(double x, double y) : x(x), y(y) {}
Point operator+(const Point& a, const Point& b) {
    return Point(a.x + b.x, a.y + b.y);
}
Point operator-(const Point& a, const Point& b) {
    return Point(a.x - b.x, a.y - b.y);
}


// Ball definitions
Ball::Ball(Point& pos, double vx, double vy, double r) : pos(pos), vx(vx), vy(vy), r(r) {}
Point Ball::getCollisionPoint() {return pos;}


// Ring definitions
Ring::Ring(Point& pos, double r, double w, double t) : pos(pos), r(r), w(w), t(t) {}

// Finds closest point on ring to certain point
Point Ring::getCollisionPoint(const Point& point) {
    if (point.x - pos.x == 0) {
        if (abs(point.y-r) <= abs(point.y+r)) {
            return Point(point.x, pos.y+r);
        } else {
            return Point(point.x, pos.y-r);
        }
    }

    // Slope of line through point and ring
    double m = (point.y - pos.y)/(point.x - pos.x);
    double b = point.y - m*point.x;

    // Find intersection of line and ring
    double D = pow((m*b)/(1 + pow(m,2)), 2) - (pow(b,2) - pow(r,2))/(1 + pow(m,2)); // discriminant
    double xMin = -m*b/(1 + pow(m,2)) + sqrt(D);
    double xMax = -m*b/(1 + pow(m,2)) - sqrt(D);

    // Choose correct x coord and find corresponding y coord. 
    if (abs(xMin - point.x) <= abs(xMax - point.x)) {
        return Point(xMin, m*xMin + b);
    } else if (abs(xMin - point.x) > abs(xMax - point.x)) {
        return Point(xMax, m*xMax + b);
    }
}
