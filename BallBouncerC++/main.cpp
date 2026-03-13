#include <QApplication>
#include <QColor>
#include <QLabel>
#include <QLayout>
#include <QLineEdit>
#include <QMainWindow>
#include <QObject>
#include <QPainter>
#include <QPen>
#include <QPushButton>
#include <QTimer>
#include <QWidget>
#include <stdio.h>
#include "common.h"

#define g -200
#define dt 0.01
double t {0}; // time


// CLASSES 
class DrawingWidget : public QWidget {

public: 
    std::vector<Ball> ballList{};

    DrawingWidget(QWidget* parent) : QWidget(parent) {
        setWindowTitle("Test");
        setGeometry(100, 100, 800, 600);

        QTimer *timer = new QTimer(this);
        connect(timer, &QTimer::timeout, this, QOverload<>::of(&MainWindow::update));
        timer->start((int)(1000*dt));
    }

    void paintEvent() {
        QPainter* painter = new QPainter(this);
        painter->fillRect(rect(), QColor(41, 41, 41, 255));
        painter->translate(static_cast<int>(width()/2), static_cast<int>(height()/2));
        painter->scale(1.5, -1.5);

        QPen* pen = new QPen();
        painter->setPen(*pen);

        QColor ballColor;
        int i = 0;
        for (Ball ball : ballList) {
            ballColor.setHsl(static_cast<int>(++i*18), 200, 160);
            pen->setColor(ballColor);
            pen->setWidth(ball.r);
            painter->drawEllipse(int(ball.pos.x)-int(0.5*ball.r), int(ball.pos.y)-int(0.5*ball.r), int(ball.r), int(ball.r));
        }
    }

    void simLoop() {
        for (Ball ball : ballList) {
            loop()
        }
    }
};


class MainWindow : public QMainWindow {
    Q_OBJECT

public: 
    MainWindow(QWidget* parent = nullptr) : QMainWindow(parent) {
        setWindowTitle("Ball Bouncer");
        resize(1000, 800);
        setMinimumSize(900, 700);

        // Timer for updating canvas
        QTimer *timer = new QTimer(this);
        connect(timer, &QTimer::timeout, this, QOverload<>::of(&MainWindow::update));
        timer->start(int(1000*dt));

        // Central widget
        QWidget* centralWidget = new QWidget(this);
        QHBoxLayout* centralWidgetLayout = new QHBoxLayout(this);

        // Canvas
        DrawingWidget* canvas = new DrawingWidget(this);

        // Sidebar
        QWidget* sidebar = new QWidget(this);
        QVBoxLayout* sidebarLayout = new QVBoxLayout(this);
        QWidget* coordWidget = new QWidget(this);

        QLabel* ballLabel = new QLabel(this);
        ballLabel->setText("Amount of balls: ");
        sidebarLayout->addWidget(ballLabel);

        // Ball initial condition input fields
        QLabel* xLabel = new QLabel(this);
        QLineEdit* xBox = new QLineEdit(this);
        xBox->setText("x:");
        QLabel* yLabel = new QLabel(this);
        QLineEdit* yBox = new QLineEdit(this);
        yBox->setText("y:");
        QLabel* vxLabel = new QLabel(this);
        QLineEdit* vxBox = new QLineEdit(this);
        vxBox->setText("vx:");
        QLabel* vyLabel = new QLabel(this);
        QLineEdit* vyBox = new QLineEdit(this);
        vyBox->setText("vy:");
        QLabel* rLabel = new QLabel(this);
        QLineEdit* rBox = new QLineEdit(this);
        rBox->setText("r:");

        // Position input elements
        QGridLayout* coordWidgetLayout = new QGridLayout(this);
        coordWidgetLayout->addWidget(xLabel, 0, 0);
        coordWidgetLayout->addWidget(xBox, 0, 1);
        coordWidgetLayout->addWidget(yLabel, 1, 0);
        coordWidgetLayout->addWidget(yBox, 1, 1);
        coordWidgetLayout->addWidget(vxLabel, 2, 0);
        coordWidgetLayout->addWidget(vxBox, 2, 1);
        coordWidgetLayout->addWidget(vyLabel, 3, 0);
        coordWidgetLayout->addWidget(vyBox, 3, 1);
        coordWidgetLayout->addWidget(rLabel, 4, 0);
        coordWidgetLayout->addWidget(rBox, 4, 1);
        coordWidget->setLayout(coordWidgetLayout);
        sidebarLayout->addWidget(coordWidget);

        // Button to add balls
        QPushButton* addButton = new QPushButton(this);
        connect(addButton, &QPushButton::clicked, this, &MainWindow::addBall);
        
        sidebar->setLayout(sidebarLayout);
        sidebar->setMaximumWidth(200);
        // sidebarLayout->setAlignment(Alignmen)

        centralWidgetLayout->addWidget(sidebar);
        // centralWidgetLayout->addWidget()
    }

    void addBall() {
        
    }
};

/////////////// FUNCTIONS ///////////////////
bool checkCollision(Ring& ring, Ball& ball) {
    Point ringCol = ring.getCollisionPoint(ball.getCollisionPoint());
    Point ballCol = ball.getCollisionPoint();
    double d = sqrt(pow((ringCol.x - ballCol.x), 2) + pow((ringCol.y - ballCol.y), 2));

    if (d <= abs(ring.r + 0.95*ball.r)) {
        return true;
    } else {
        return false;
    }
}


Point collision(Ring& ring, Ball& ball) {
    double phi = atan2(ball.pos.y - ring.pos.y, ball.pos.x-ring.pos.x);
    double beta = M_PI/2 - phi;

    double vn0 = ball.vx*cos(phi) + ball.vy*sin(phi);
    double vt0 = ball.vx*sin(phi) - ball.vy*cos(phi);

    double vn = -vn0*ball.e;
    double vt = vt0;

    double vx = vn*cos(phi) + vt*sin(phi);
    double vy = vn*sin(phi) - vt*cos(phi);

    return Point(vx, vy);
}


void loop(Ball& ball, Ring& ring) {
    double vx = ball.vx;
    double vy = ball.vy;

    // Collision
    if (checkCollision(ring, ball)) {
        Point vNew = collision(ring, ball);
        vx = vNew.x;
        vy = vNew.y;
    }

    // Gravity 
    vy = vy + g*dt;

    ball.vx = vx;
    ball.vy = vy;

    // Update position
    ball.pos.x = ball.pos.x + ball.vx*dt;
    ball.pos.y = ball.pos.y + ball.vy*dt;

    // Ensure balls cannot escape ring
    double phi = atan2(ball.pos.y - ring.pos.y, ball.pos.x-ring.pos.x);
    if (sqrt(pow((ball.pos.x - ring.pos.x), 2) + pow((ball.pos.y - ring.pos.y), 2))) {
        ball.pos.x = (ring.r - ring.t - ball.r)*cos(phi);
        ball.pos.y = (ring.r - ring.t - ball.r)*sin(phi);
    }

    t = t + dt;  
}


int main(int argc, char *argv[]) {
    QApplication app (argc, argv);
    MainWindow window;
    window.show();
    return app.exec();
}


#include "main.moc"
