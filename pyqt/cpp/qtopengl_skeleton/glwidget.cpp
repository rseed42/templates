#include <QtGui>
#include <QtOpenGL>
#include "glwidget.h"
//------------------------------------------------------------------------------
// GL Widget
//------------------------------------------------------------------------------
GLWidget::GLWidget(QWidget *parent) : QGLWidget(parent){
    wndSize = QSize(600,600);
    setFixedSize(wndSize);
}
//------------------------------------------------------------------------------
GLWidget::~GLWidget(){

}
//------------------------------------------------------------------------------
void GLWidget::initializeGL(){
  glShadeModel(GL_SMOOTH);
  glClearColor(0.0f, 0.0f, 0.0f, 0.0f);
  glClearDepth(1.0);
  glEnable(GL_DEPTH_TEST);
  glDepthFunc(GL_LEQUAL);
  glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
}
//------------------------------------------------------------------------------
void GLWidget::paintGL(){
  // Set up
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glLoadIdentity();
  glTranslatef(0.0, 0.0, -1);
  // Draw
  glBegin(GL_TRIANGLES);
  glColor3f(1.0f, 0.0f, 0.0f);
  glVertex3f(0.0f, 0.0f, 0.0f);
  glColor3f(0.0f, 1.0f, 0.0f);
  glVertex3f(1.0f, 0.0f, 0.0f);
  glColor3f(0.0f, 0.0f, 1.0f);
  glVertex3f(1.0f, 1.0f, 0.0f);
  glEnd();
}
//------------------------------------------------------------------------------
void GLWidget::resizeGL(int width, int height){
    int side = qMin(width, height);
    glViewport((width - side) / 2, (height - side) / 2, side, side);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, 1, 0, 1, -1, 1);
    glMatrixMode(GL_MODELVIEW);
}
