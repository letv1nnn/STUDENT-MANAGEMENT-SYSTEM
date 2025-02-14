import psycopg2
from send_email import send, UserModel
import asyncio
import time


class Student(object):
    def __init__(self, name: str, surname: str, age: int, grade: str, email: str):
        self.name = name
        self.surname = surname
        self.age = age
        self.grade = grade
        self.email = email

    def __eq__(self, other):
        return self.email == other.email


def exist(cur: psycopg2.extensions.cursor, student: Student):

    cur.execute(
        '''
        SELECT 1 FROM students
        WHERE name = %s AND surname = %s
        ''',
        (student.name, student.surname)
    )

    ex = cur.fetchone()
    return ex


def add(cur: psycopg2.extensions.cursor, student: Student) -> None:

    if exist(cur, student):
        print("⚠️ Student already exists. Skipping insert.")
        return

    cur.execute(
        f'''
        INSERT INTO students (name, surname, age, grade, email) VALUES
        (%s, %s, %s, %s, %s)
        ''',
        (student.name, student.surname, student.age, student.grade, student.email)
    )

    print("✅ Student added successfully!")


def view_student_list(cur: psycopg2.extensions.cursor) -> None:
    cur.execute(
        '''
        SELECT * FROM students
        '''
    )
    for row in cur.fetchall():
        print(row)


def update_student_info(cur: psycopg2.extensions.cursor, student: Student, new_value, column) -> None:
    allowed_columns = {"name", "surname", "age", "grade", "email"}
    if column not in allowed_columns:
        print(f"⚠️ Invalid column name: {column}")
        return

    if not exist(cur, student):
        print('⚠️ Provided student does not exist!')
        return

    cur.execute(
        '''
        UPDATE students
        SET {} = %s
        WHERE name = %s and surname = %s
        '''.format(column),
        (new_value, student.name, student.surname)
    )
    print("✅ Student info updated successfully.")


def delete(cur: psycopg2.extensions.cursor, student: Student) -> None:

    if not exist(cur, student):
        print('⚠️ Provided student does not exist!')
        return
    cur.execute(
        '''
        DELETE FROM students
        WHERE email = %s
        ''',
        (student.email,)
    )

    cur.connection.commit()
    print("✅ Student has been deleted.")


def search_for_student(cur: psycopg2.extensions.cursor, student: Student) -> None:

    if not exist(cur, student):
        print('⚠️ Provided student does not exist!')
        return
    cur.execute(
        '''
        SELECT * FROM students
        WHERE email = %s
        ''',
        (student.email,)
    )

    st = cur.fetchone()
    for i in st:
        print(f'---> {i:^12}')


def report(cur: psycopg2.extensions.cursor) -> None:  # total number of students, average age per grade, etc.
    print('REPORT')
    cur.execute(
        '''
        SELECT COUNT(*) FROM students
        '''
    )
    print('Total number of students is', cur.fetchone()[0])

    cur.execute(
        '''
        SELECT AVG(age) FROM students
        '''
    )
    print('Average age is', round(cur.fetchone()[0]))

    cur.execute(
        '''
        SELECT AVG(
        CASE 
            WHEN grade = 'A' THEN 4.0
            WHEN grade = 'B' THEN 3.0
            WHEN grade = 'C' THEN 2.0
            WHEN grade = 'D' THEN 1.0
            WHEN grade = 'F' THEN 0.0
        END
        ) AS average_grade FROM students;
        '''
    )
    print('Average grade is', round(cur.fetchone()[0]))


def auto_send_mail(cur: psycopg2.extensions.cursor):
    cur.execute('''
        SELECT students.name, students.email FROM students
        WHERE grade = 'D' OR grade = 'F' OR grade = 'D-' OR grade = 'F-' OR grade = 'F+'
    ''')
    students = cur.fetchall()

    async def send_one(student):
        email = UserModel(email=student[-1])
        name = student[0]
        await asyncio.to_thread(send, email, name)

    async def execution():
        tasks = [send_one(student) for student in students]
        await asyncio.gather(*tasks)

    asyncio.run(execution())


def main():
    try:
        with psycopg2.connect(
            host='ur db',
            dbname='ur db',
            user='ur db',
            password='ur db',
            port= "port u use, initialy it's 5432"
        ) as conn:
            cur = conn.cursor()
            st = Student('Monica', 'Albreight', 22, 'D-', 'monica@gmail.com')

            start = time.time()
            # Commands field...
            add(cur, st)
            view_student_list(cur)
            auto_send_mail(cur)

            print('Executing time: ' + (str(time.time() - start))[:6] + 'sec.')

    except Exception as e:
        print(f"Issue with: {e}")


if __name__ == '__main__':
    main()
