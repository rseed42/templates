#ifndef GLWIDGET_H
#define GLWIDGET_H
#include <QGLWidget>
//------------------------------------------------------------------------------
// GLWidget
//------------------------------------------------------------------------------
class GLWidget : public QGLWidget{
    Q_OBJECT

public:
    GLWidget(QWidget *parent = 0);
    ~GLWidget();

protected:
    void initializeGL();
    void paintGL();
    void resizeGL(int width, int height);

private:
    QSize wndSize;
};

#endif
