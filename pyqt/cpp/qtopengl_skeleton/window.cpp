#include <QtGui>
#include "glwidget.h"
#include "window.h"
//------------------------------------------------------------------------------
// Main Window
//------------------------------------------------------------------------------
Window::Window(){
    glWidget = new GLWidget;
    setCentralWidget(glWidget);
    setWindowTitle(tr("OpenGL Qt4 C++ Template"));
}
void Window::keyPressEvent(QKeyEvent *e){
    if (e->key() == Qt::Key_Q)
        close();
    else
        QWidget::keyPressEvent(e);
}
