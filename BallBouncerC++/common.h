struct Point {
    double x, y;
    Point();
    Point(double x, double y);
};


struct Ball {
    Point pos;
    double vx, vy, r;
    double e = 0.95;

    Ball(Point& pos, double vx, double vy, double r);
    Point getCollisionPoint();
};


struct Ring {
    Point pos;
    double w, t, r;

    Ring(Point& pos, double r, double w, double t);
    Point getCollisionPoint(const Point& point);
};