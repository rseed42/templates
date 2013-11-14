#ifndef WINDOW_H
#define WINDOW_H
#include <QMainWindow>
class GLWidget;
//------------------------------------------------------------------------------
// Main Window
//------------------------------------------------------------------------------
class Window : public QMainWindow{
    Q_OBJECT

public:
    Window();

protected:
    void keyPressEvent(QKeyEvent *event);

private:
    GLWidget *glWidget;
};

#endif
