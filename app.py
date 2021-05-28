from flask import Flask,render_template,g,request
from database import get_db,connect_db
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True



@app.teardown_appcontext
def db_close(error):
   if hasattr(g,'sqlite3_db'):
      g.sqlite3_db.close() 
            

@app.route('/',methods=['GET','POST'])
def home():
   db = get_db()
   if request.method == 'POST' :
      date = request.form['date'] # date in YYYY-MM-DD format
      dt = datetime.strptime(date,'%Y-%m-%d')
      database_date = datetime.strftime(dt,'%Y%m%d')
      db.execute('insert into log_date(entry_date) values(?)',[database_date])
      db.commit()
   
   cur = db.execute('select log_date.entry_date,sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat,sum(food.calories) as calories from log_date left join food_date on food_date.log_date_id = log_date.id left join food on food.id = food_date.food_id group by log_date.entry_date order by log_date.entry_date desc')
   result = cur.fetchall()
   pretty_result = []

   for data in result:
      single_date = {}
      single_date['date'] = data['entry_date']
      single_date['protein'] = data['protein']
      single_date['carbohydrates'] = data['carbohydrates']
      single_date['fat'] = data['fat']
      single_date['calories'] = data['calories']
      d = datetime.strptime(str(data['entry_date']),'%Y%m%d')
      single_date['entry_date'] = datetime.strftime(d,'%B %d, %Y')
      pretty_result.append(single_date)
   #print(pretty_result)

   return render_template('home.html',result=pretty_result)

@app.route('/view/<date>',methods=['GET','POST'])
def view(date):
   db = get_db()

   cur = db.execute('select id,entry_date from log_date where entry_date = ?',[date])
   date_result = cur.fetchone()

   if request.method == 'POST':
      db.execute('insert into food_date (food_id,log_date_id) values (?,?)',[request.form['food-select'],date_result['id']])
      db.commit()      

   d = datetime.strptime(str(date_result['entry_date']),'%Y%m%d')
   prety_date = datetime.strftime(d,'%B %d, %Y')

   food_cur = db.execute('select id,name from food')
   food_result = food_cur.fetchall()

   log_cur = db.execute('select food.name,food.protein,food.carbohydrates,food.fat,food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?',[date])
   log_result = log_cur.fetchall()

   totals = {}
   totals['protein'] = 0
   totals['carbohydrates'] = 0
   totals['fat'] = 0
   totals['calories'] = 0

   for food in log_result:
      totals['protein']+=food['protein']
      totals['carbohydrates']+=food['carbohydrates']
      totals['fat']+=food['fat']
      totals['calories']+=food['calories']


   return render_template('day.html',entry_date=date_result['entry_date'],date=prety_date,food_result=food_result,log_result=log_result,total=totals)

@app.route('/food',methods=['GET','POST'])
def food():
   db =get_db()
   if request.method == 'POST':
      name = request.form['food-name']
      protein = int(request.form['protein'])
      carbohydrates = int(request.form['carbohydrates'])
      fat = int(request.form['fat'])

      calories = protein * 4 + carbohydrates * 4 + fat * 9
      
      db.execute('insert into food(name,protein,carbohydrates,fat,calories) values (?,?,?,?,?)',\
         [name,protein,carbohydrates,fat,calories])
      db.commit()
   
   cur = db.execute('select name,protein,carbohydrates,fat,calories from food')
   result = cur.fetchall()
   return render_template('add_food.html',result = result)


if __name__ == "__main__":
    app.run()