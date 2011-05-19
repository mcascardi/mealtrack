import cgi
import os
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Meal(db.Model):
  user = db.UserProperty(required=True)
  food = db.StringProperty(required=True)
  category = db.CategoryProperty(required=True)
  datetime = db.DateTimeProperty(auto_now_add=True)

def user_key(user_name=None):
  return db.Key.from_path('User', user_name)

class Expense(db.Model):
  user = db.UserProperty(required=True)
  amount = db.FloatProperty(required=True)
  item = db.StringProperty(required=True)
  date = db.DateProperty(auto_now_add=True)
  used = db.BooleanProperty(False)
  usedate = db.DateProperty()

def get_meals(user):
  query = Meal.all()
  query.filter('user = ',user)
  return query

def get_expenses(user):
  query = Expense.all()
  query.filter('user = ',user)
  return query

class Greeting(webapp.RequestHandler):
  def get(self):
    if users.get_current_user():
      self.redirect('/home')
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      values = {
        'url_linktext': url_linktext,
        'url': url
        }
      self.response.out.write(template.render(path,values))

class MainPage(webapp.RequestHandler):
  def get(self):
    if users.get_current_user():
      user = users.get_current_user()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
      meals_qry = get_meals(user)
      expenses_qry = get_expenses(user)
      meals = meals_qry.fetch(10)
      expenses = expenses_qry.fetch(10)
      cost = 0
      for expense in expenses:
        cost += expense.amount
      path = os.path.join(os.path.dirname(__file__), 'template.html')
      values = {
        'cost' : cost,
        'user' : user,
        'meals' : meals,
        'expenses' : expenses,
        'url': url,
        'url_linktext': url_linktext
        }
      self.response.out.write(template.render(path,values))
    else:
      self.redirect('/')

class AddExpense(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    amount = float(self.request.get('amount'))
    item = self.request.get('item')
    expense = Expense(user=user,amount=amount,item=item)
    expense.put()
    self.redirect('/home')

class AddMeal(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    food = self.request.get('food')
    category = self.request.get('category')
    meal = Meal(user=user,food=food,category=category)
    meal.put()
    self.redirect('/home')

class UseExpense(webapp.RequestHandler):
  def post(self):
    expense_key = self.request.get('expense')
    if expense_key:
      expense = Expense.get(expense_key)
      if not expense:
        self.redirect('/home')
      else:
        self.redirect('/home')
    if expense:
      expense.used = True
      if self.request.get('usedate'):
        expense.usedate = self.request.get('usedate')
      expense.put()

application = webapp.WSGIApplication([
  ('/', Greeting),
  ('/home', MainPage),
  ('/add-meal', AddMeal),
  ('/add-expense', AddExpense),
  ('/use-expense', UseExpense)
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
