import tkinter as tk
#from tkinter import Tk, Button
from tkinter import ttk
import cv2
import face_recognition
import dlib
import numpy as np
import tkinter.font as tkFont
import pymysql
#creating an account number and otp
import random
import requests
from datetime import datetime, timedelta
import tkinter.messagebox as messagebox
#sending history to email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pdfkit
import tempfile
import subprocess

class Face_Recog_project:
    def __init__(self, master):
        self.master = master
        master.geometry("500x500")
        master.configure(bg="beige")
        master.title("On-start Window")

        # make the window not resizable
        master.resizable(False, False)

        # Create a frame to hold the text and buttons
        self.frame = tk.Frame(master, width=200, height=200, bg="beige")
        self.frame.pack(expand=True, padx=20, pady=20, anchor= tk.CENTER)

        # Create the first buttons
        self.button1 = tk.Button(self.frame, text="Login", fg="black", bd=0, bg="white",command=self.login_access)
        self.button1.pack(side=tk.LEFT, padx=30)

        # Create the second button
        self.button2 = tk.Button(self.frame, text="Register!", fg="black", bd=0, bg="white", command=self.register_access)
        self.button2.pack(side=tk.LEFT, padx= 30)
 
    def login_access(self):
        login_window = tk.Toplevel()
        login_app = LoginWin(login_window)

    def register_access(self):
        register_window = tk.Toplevel()
        register_app = RegisterWin(register_window)

class LoginWin:
    def __init__(self, master):
        self.otp = random.randint(100000, 999999)
        self.master = master
        master.geometry("400x400")
        master.configure(bg= "white")
        master.title("Login Window")  

        # make the window not resizable
        master.resizable(False, False)  

        #create a frame for both entry and label
        self. framelog = tk.Frame(master, bg= "beige")
        self. framelog.pack(expand=True, fill=tk.BOTH, padx=20, pady=20, anchor= tk.CENTER) 
        self.intro_label = tk.Label(self.framelog, text = "Enter your account number", bg = "beige", fg= "brown")
        self.intro_label.pack(padx=20, pady=20)

        #create a label for inputting account number
        self.acc_num_label = tk.Label(self.framelog, text= "Account Number:", bg="beige", fg= "brown")
        self.acc_num_label.pack( padx=25, pady=20)
        self.acc_num_entry = tk.Entry(self.framelog, bg= "beige", fg="brown")
        self.acc_num_entry.pack( padx= 25, pady=2)

        #button verifies the account number and sends the otp so there will be two uses
        self.butn_send_otp = tk.Button(self.framelog, text="Send OTP", fg="brown", bd=0, bg="white", command= self.otp_send)
        self.butn_send_otp.pack(padx=30, pady= 30)

    #hostpinnacle API goes here to send the otp to users phone
    def hostpinn(self,phone_no,otp):

        #over here im calling or accessing variables of another function - function otp_send 
        self.ottp = otp
        self.nambari = phone_no

        #hospinnacle
        url = "https://smsportal.hostpinnacle.co.ke/SMSApi/send"
        headers = {"Content-Type": "application/json"}
        data = {
            "userid": "Nyambura",
            "password": "9kgEQkc0",
            "senderid": "HPKSMS",
            "msgType": "text",
            "duplicatecheck": "true",
            "sendMethod": "quick",
            "sms": [
                {
                    "mobile": [self.nambari],
                    "msg": f"Your OTP is {self.ottp}"
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            messagebox.showinfo("OTP Sent", "An OTP has been sent.")
        else:
            messagebox.showerror("Error", "Failed to send OTP")
        print(response.content)

    #button that sends otp and verifies users account no
    def otp_send(self):
        connection = pymysql.connect(host='localhost',
                             user='root',
                             password='52456',
                             db='mydatabase')

        # Insert some data
        cursor = connection.cursor()
        with connection.cursor() as cursor:
            account = self.acc_num_entry.get()
       
            sql = "SELECT phone_number, account_number FROM bank_users WHERE account_number = %s"
            cursor.execute(sql, (account,))
            result = cursor.fetchone()
           
            #check if the account numbers match
            if result is not None:# and result[1] != account:     
                if result[1] != account:            
                    messagebox.showerror("Access denied", "Invalid account number")
                
                    # clear the previous entry
                    self.acc_num_entry.delete(0, 'end')  # 'end' means the end of the entry widget
                else:

                    #variable to send otp
                    self.otp = random.randint(100000, 999999)
                    pswd = self.otp
                    self.phone_no = result[0]

                    #print otp 
                    print(pswd)

                    #add into database the new otp
                    query = "UPDATE bank_users SET otp = %s WHERE account_number = %s"
                    cursor.execute(query, (pswd, account))
                    # commit the changes
                    connection.commit()
                
                    #send the stored otp to users phone 
                    self.hostpinn(self.phone_no, self.otp)

                    #destroy previous window
                    self.master.destroy()

                    otp_window = tk.Toplevel()
                    otp_app = otpWin(otp_window, self.phone_no, account)
            else:
                messagebox.showerror("Access denied", "Invalid account number")
                self.acc_num_entry.delete(0, 'end')  # clear the previous entry

class otpWin:
    def __init__(self, master, phone_no, account):
        self.master = master
        self.account = account
        master.geometry("400x400")
        master.configure(bg= "white")
        master.title("OTP Window")

        #initialize counter for failed attempts
        self.incorrect_otp = 0

        # make the window not resizable
        master.resizable(False, False)

        #create a frame for both entry and label
        self. frames = tk.Frame(master, bg= "beige")
        self. frames.pack(expand=True, fill=tk.BOTH, padx=20, pady=20, anchor= tk.CENTER)
        self.otp_label = tk.Label(self.frames, text = "Enter the sent OTP", bg = "beige", fg= "brown")
        self.otp_label.pack(padx=20, pady=20)

        #create a label for inputting account number
        self.otp_label = tk.Label(self.frames, text= "OTP Password:", bg="beige", fg= "brown")
        self.otp_label.pack( padx=25, pady=20)
        self.otp_entry = tk.Entry(self.frames, bg= "beige", fg="brown")
        self.otp_entry.pack( padx= 25, pady=2)
        self.butn_verify_otp = tk.Button(self.frames, text="Verify OTP", fg="brown", bd=0, bg="white", command= self.otp_verify)
        self.butn_verify_otp.pack(padx=30, pady= 30)

    #verify the face or in other words do face verification
    def verify(self, accnt):
        self.account= accnt
        
        # Connect to the MySQL database
        db = pymysql.connect(host='localhost', user='root', password='52456', database='mydatabase')
        cursor = db.cursor()

        def load_reference_embedding(cursor, account_number):
            # Load the reference face embedding from the database for the given account number
            query = "SELECT face_embedding FROM face_db WHERE account_number = %s"
            cursor.execute(query, (account_number,))
            result = cursor.fetchone()

            if result:
                embedding_str = result[0]
                embedding = np.fromstring(embedding_str, sep=' ')
                return embedding.reshape(-1, 128)
            else:
                return None


        def compare_face_embeddings(face_embedding, reference_embedding):
            # Compute the distance between the face embeddings
            if reference_embedding is not None:
                distance = np.linalg.norm(face_embedding - reference_embedding)
                if distance < 0.6:
                    return True
            return False


        def face_verification(cursor, connection, account_number):
            # Start the webcam for capturing images
            video_capture = cv2.VideoCapture(0)

            while True:
                # Capture frame-by-frame
                ret, frame = video_capture.read()

                # Convert the image from BGR color (OpenCV default) to RGB color
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Detect faces in the frame
                face_locations = face_recognition.face_locations(rgb_image)

                # If no face is detected, continue to the next frame
                if len(face_locations) == 0:
                    cv2.imshow('Video', frame)
                    cv2.waitKey(1)
                    continue
                
                # Get the face embedding of the detected face
                face_encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]

                # Retrieve the reference embedding for the account number
                reference_embedding = load_reference_embedding(cursor, account_number)

                # Compare the face embedding with the reference embedding
                verification_result = compare_face_embeddings(face_encoding, reference_embedding)

                # Display the captured image with bounding boxes
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                if verification_result:
                    cv2.putText(frame, "Verification Successful", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Verification Failed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow('Video', frame)

                # Press 'q' to quit the program
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                video_capture.release()

            # Release the webcam and close the OpenCV windows
            video_capture.release()

            cv2.destroyAllWindows()
            connection.close()

        account_number = self.account
        face_verification(cursor, db, account_number)

        # Close the database connection
        db.close()

    #verify entered otp
    def otp_verify(self):
        connection = pymysql.connect(host='localhost',
                             user='root',
                             password='52456',
                             db='mydatabase')

        # Insert some data
        cursor = connection.cursor()
        with connection.cursor() as cursor:
            query= "SELECT otp FROM bank_users WHERE account_number = %s"
            cursor.execute(query, (self.account,))
            otp = cursor.fetchone()[0]

            pswd_ent = self.otp_entry.get()
            pswd_entry = int(pswd_ent)
            print(pswd_entry)

            if otp == pswd_entry:
                #otp expiry
                now = datetime.now()
                time_expiry = now + timedelta(seconds= 60)

                #add otp expiry to database
                sql1 = "UPDATE bank_users SET otp_expiry = %s WHERE account_number = %s"
                cursor.execute(sql1,(time_expiry, self.account))
                
                #save the changes 
                connection.commit()
                
                sqll = "SELECT otp_expiry FROM bank_users WHERE account_number = %s"
                cursor.execute(sqll, (self.account,))
                database_expiry = cursor.fetchone()[0]

                #check if time is done
                if database_expiry < now:
                    messagebox.showinfo ('ERROR', "OTP EXPIRED")
                    self.master.destroy()
                else:
                    messagebox.showinfo ('SUCCESS', "OTP VALID,  SMILE AT THE CAMERA.")

                    #destroy previous window
                    self.master.destroy()

                    #face verification of user
                    self.verify (self.account)

                    dash_window = tk.Toplevel()
                    dash_app = dashVerify(dash_window, self.account)

            else:
                self.incorrect_otp+= 1  # increment failed attempts counter

                if self.incorrect_otp == 3:
                    self.otp_entry.configure(state="disabled")  # disable OTP entry field
                    messagebox.showerror("Account Blocked", "You have reached the maximum number of failed attempts. Your account has been blocked.")
                else:
                    messagebox.showerror("ERROR", "INVALID OTP")
                    # clear the previous entry
                    self.otp_entry.delete(0, 'end')  # 'end' means the end of the entry widget

class dashVerify:
    def __init__(self, master, account):
        self.master = master
        self.account = account
        master.geometry("900x600")
        master.configure(bg= "beige")
        master.title("Dashboard Window") 

        # make the window not resizable
        master.resizable(False, False)
        
        #bold text for the word ATM
        bold_font = tkFont.Font(family="Georgia", size=13, weight=tkFont.BOLD)

        #make frames that holds the name ATM CHASE BANK AND A LOGOUT---------------------------------
        self.introducttion = tk.Frame(master, width=800, height=2, bg="beige")
        self.introducttion.pack( pady=50, anchor= tk.NW)#padx=15, pady=90, anchor= tk.NW

        self.intro_label = tk.Label(self.introducttion, text = "ATM", bg="beige", fg= "brown", font= bold_font)
        self.intro_label.grid(row=0, column=0, padx=130, pady=10)
        #self.intro_label.pack(padx=20, pady=20, side=tk.LEFT)

        self.exit_button = tk.Button(self.introducttion, text = "Log Out", bg = "#FBCFCF", fg= "black", borderwidth=0, relief="flat", width=10, command=self.log)
        self.exit_button.grid(row=0, column=1, padx=400, pady=10)
        #self.exit_button.pack( padx=350, side=tk.LEFT)

        connection = pymysql.connect(host='localhost',
                             user='root',
                             password='52456',
                             db='mydatabase')

        # get some data
        cursor = connection.cursor()
        with connection.cursor() as cursor:
            query = "SELECT name FROM bank_users WHERE account_number = %s"
            cursor.execute(query, (self.account,))
            name = cursor.fetchone()[0]
        connection.close()

        # create a frame for left side to hold name and balance---------------------------------------------------------
        self.framey = tk.Frame(master, width=200, height=200, bg="white")
        self.framey.pack(side=tk.LEFT, padx=100, anchor=tk.NW)#expand=True, padx=20, pady=20, 

        self.label = tk.Label(self.framey, text= "Welcome", bg = "white", fg= "brown")
        self.label.pack(padx=20, pady=20)

        self.name = tk.Label(self.framey, text= name, bg = "white", fg= "#808080")
        self.name.pack(padx=20, pady=20)

        connection = pymysql.connect(host='localhost',
                             user='root',
                             password='52456',
                             db='mydatabase')

        # get some data
        cursor = connection.cursor()
        with connection.cursor() as cursor:
            query = "SELECT acc_balance FROM bank_users WHERE account_number = %s"
            cursor.execute(query, (self.account,))
            amount = cursor.fetchone()[0]
        
        self.amount = amount

        #amount in the bank
        self.amountt = tk.Label(self.framey, text= "Balance:", bg = "white", fg= "brown")
        self.amountt.pack(padx=20, pady=20)

        self.db_amount = tk.Label(self.framey, text= amount, bg = "white", fg= "#808080")
        self.db_amount.pack(padx=20, pady=20)

        #amount one can withdraw
        if amount is not None and int(amount) > int(40000):
            amount2= int(40000) - amount
            #available for withdraw
            self.amount_withdrawable = tk.Label(self.framey, text= "Amount Usable:", bg = "white", fg= "brown")
            self.amount_withdrawable.pack(padx=20, pady=20)

            self.db_amount_with = tk.Label(self.framey, text= amount2, bg = "white", fg= "#808080")
            self.db_amount_with.pack(padx=20, pady=20)
        else:
            self.amounts = tk.Label(self.framey, text= "Amount Usable:", bg = "white", fg= "brown")
            self.amounts.pack(padx=20, pady=20)

            self.db_amount = tk.Label(self.framey, text= amount, bg = "white", fg= "#808080")
            self.db_amount.pack(padx=20, pady=20)

        #frames to hold choices one can make in the atm----------------------------------------------------
        self.options = tk.Frame(master, width=200, height=500, bg="#F5F5E6")
        self.options.pack(side=tk.LEFT, pady=100, anchor=tk.NE)
               
        self.withdraw = tk.Button(self.options, text= "Withdraw",bg = "beige", fg= "brown", width=10, border= 0, command= self.withdrawal)
        self.withdraw.grid(row=0, column=0, padx=10, pady=10)
        #self.withdraw.pack(side=tk.LEFT ,padx=10)

        self.deposit =tk.Button(self.options, text="Deposit", bg = "beige", fg= "brown", width=10, border= 0, command= self.deposition)
        self.deposit.grid(row=0, column=1, padx=10, pady=10)
        #self.deposit.pack(side=tk.LEFT ,padx=10)

        self.payments = tk.Button(self.options, text="Payments", bg = "beige", fg= "brown", width=10, border=0, command= self.history)#load history for this one 
        self.payments.grid(row=0, column=2, padx=10, pady=10) 
        #self.payments.pack(side=tk.LEFT ,padx=10)

        self.credit_card = tk.Button(self.options, text="Credit Card",bg = "beige", fg= "brown", width=10, border=0)
        self.credit_card.grid(row=1, column=0, padx=10, pady=10) 
        #self.credit_card.pack(side=tk.LEFT ,padx=10)

        self.account_settings = tk.Button(self.options, text="Account Settings",bg = "beige", fg= "brown", width=12, borderwidth=0, relief="flat")
        self.account_settings.grid(row=1, column=1, padx=10, pady=10) 
        #self.account_settings.pack(side=tk.LEFT ,padx=10)
        print(self.amount)

    def withdrawal(self):
        if self.amount <= 0 :
            #if self.amount == 0:
            messagebox.showerror("Error", "Insufficient Balance")
            return
        else:
            withdraw_window = tk.Toplevel()
            withdraw_app = WithdrawWin(withdraw_window, self.amount, self.account)#, self.data_amount
    
    def deposition(self):
        deposit_window = tk.Toplevel()
        deposit_app = DepositWin(deposit_window, self.amount, self.account)

    #this window will lead the user into a detailed account on his previous transactions
    def history(self):
        history_window = tk.Toplevel()
        history_app = HistoryWin(history_window, self.account)

    #logout button
    def log(self):
        self.master.destroy()

class WithdrawWin:
    def __init__(self, master, amount, account):
        self.master = master
        self.account = account
        self.amount = amount
        master.geometry("400x400")
        master.configure(bg="beige")
        master.title("Withdraw window")

        # make the window not resizable
        master.resizable(False, False)

        #create a frame for both entry and label
        self. frame_amnt = tk.Frame(master, bg= "beige")
        self. frame_amnt.pack(expand=True, fill=tk.BOTH, padx=20, pady=20, anchor= tk.CENTER) 

        self.amnt_label = tk.Label(self.frame_amnt, text = "Enter Amount To Withdraw", bg = "beige", fg= "brown")
        self.amnt_label.pack(padx=20, pady=20)

        #create a label for inputting account number
        self.amnt_label = tk.Label(self.frame_amnt, text= "Amount:", bg="beige", fg= "brown")
        self.amnt_label.pack( padx=25, pady=20)
        self.amnt_entry = tk.Entry(self.frame_amnt, bg= "beige", fg="brown")
        self.amnt_entry.pack( padx= 25, pady=2)

        #button verifies the account number and sends the otp so there will be two uses
        self.butn_withdraw = tk.Button(self.frame_amnt, text="Withdraw", fg="brown", bd=0, bg="white", command= self.toa)
        self.butn_withdraw.pack(padx=30, pady= 30)

    def toa(self):
        minus = self.amnt_entry.get()

        #check if the amount is valid
        if not minus or not minus.isdigit():
            messagebox.showerror("Error", "Please enter a valid number.")
            return
        else:
            newww = self.amount - int(minus)

        #validate if the amount entered has exceeded that in the account
        if int(minus) > self.amount: 
            messagebox.showerror("ERROR", "Input doesn't match Balance")
            self.amnt_entry.delete(0, 'end')
        else:
            connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='52456',
                                 db='mydatabase')

            # get some data
            cursor = connection.cursor()
            with connection.cursor() as cursor:
                query = "UPDATE bank_users SET acc_balance = %s WHERE account_number = %s"
                cursor.execute(query, (newww, self.account))
                
                #gets the time of withdrawal
                withdrawal_time  = datetime.now()
                prefix = '1457'
                ident = prefix + ''.join(random.choices('0123456789', k=4))
                #UPDATES TRANSACTIONS TABLE
                cursor.execute("INSERT INTO transactions (account_number, transaction_id, transaction_date, transaction_type, transaction_amount) VALUES (%s, %s,%s, %s, %s)", (self.account, ident, withdrawal_time, "Withdrew", minus))

            #save the changes
            connection.commit()
            #display success message
            messagebox.showinfo("SUCCESS", f"You have withdrawn {minus} from your account")
            #destroy previous window
            self.master.destroy()

class DepositWin:
    def __init__(self, master, amount, account):
        self.master = master
        self.account = account
        self.data_amount = amount
        master.geometry("400x400")
        master.configure(bg="beige")
        master.title("Deposit window")

        # make the window not resizable
        master.resizable(False, False)

        #create a frame for both entry and label
        self. frame_deposit = tk.Frame(master, bg= "beige")
        self. frame_deposit.pack(expand=True, fill=tk.BOTH, padx=20, pady=20, anchor= tk.CENTER) 

        self.amnt_label = tk.Label(self.frame_deposit, text = "Enter Amount To Deposit", bg = "beige", fg= "brown")
        self.amnt_label.pack(padx=20, pady=20)

        #create a label for inputting account number
        self.deposit_label = tk.Label(self.frame_deposit, text= "Amount:", bg="beige", fg= "brown")
        self.deposit_label.pack( padx=25, pady=20)
        self.deposit_entry = tk.Entry(self.frame_deposit, bg= "beige", fg="brown")
        self.deposit_entry.pack( padx= 25, pady=2)

        #button verifies the account number and sends the otp so there will be two uses
        self.butn_deposit = tk.Button(self.frame_deposit, text="Deposit", fg="brown", bd=0, bg="white", command= self.weka)
        self.butn_deposit.pack(padx=30, pady= 30)

    def weka(self):
        depositions = self.deposit_entry.get()

        #validate users input for blank spaces
        if not depositions or not depositions.isdigit():
            messagebox.showerror("Error", "Please enter a valid input")
            return
        else:
            entry = self.data_amount + int(depositions)

        if int(depositions) < 0:
            messagebox.showerror("Error", "Deposit is negative shillings, be realistic")
            self.deposit_entry.delete(0, 'end')
        else:
            connection = pymysql.connect(host='localhost',
                                user='root',
                                password='52456',
                                db='mydatabase')
            # get some data
            cursor = connection.cursor()
            with connection.cursor() as cursor:
                query = "UPDATE bank_users SET acc_balance = %s WHERE account_number = %s"
                cursor.execute(query, (entry, self.account))
            #save the changes
                prefix = '1456'
                identi = prefix + ''.join(random.choices('0123456789', k=4))

                #gets the date the transaction was made
                deposit_time = datetime.now()

                #UPDATES TRANSACTIONS TABLE
                cursor.execute("INSERT INTO transactions (account_number, transaction_id, transaction_date, transaction_type, transaction_amount) VALUES (%s, %s,%s, %s, %s)", (self.account, identi, deposit_time, "Deposit", depositions))
        
            connection.commit()
            #display success message
            messagebox.showinfo("SUCCESS", f"You have deposited {depositions} to your account")
            #destroy previous window
            self.master.destroy()

class RegisterWin:
    def __init__(self, master):
        self.master = master
        master.geometry("600x600")
        master.configure(bg="white")
        master.title("Register Window")

        # make the window not resizable
        master.resizable(False, False)

        self.binvenue_label = tk.Label(master, text = "Enter Your Details", bg="white", fg= "brown")
        self.binvenue_label.pack(padx=20, pady=20, anchor=tk.CENTER)

        #create a frame and pack but place the labels and entries into grid formation-------------------------------------
        self. frame_register = tk.Frame(master, bg= "beige", width=200, height=200)
        self. frame_register.pack(pady=50) 

        #create a label for inputting account number
        self.name_label = tk.Label(self.frame_register, text= "Your full names:", bg="beige", fg= "brown")
        self.name_label.grid(row=1, column=0, padx=20, pady=20)
        self.name_entry = tk.Entry(self.frame_register, bg= "beige", fg="brown", bd=0)
        self.name_entry.grid(row=1, column=1, padx=20, pady=20)

        self.email_label = tk.Label(self.frame_register, text= "Your email:", bg="beige", fg= "brown")
        self.email_label.grid(row=2, column=0, padx=20, pady=20)
        self.email_entry = tk.Entry(self.frame_register, bg= "beige", fg="brown")
        self.email_entry.grid(row=2, column=1, padx=20, pady=20)

        self.phone_no_label = tk.Label(self.frame_register, text= "Your Phone Number:", bg="beige", fg= "brown")
        self.phone_no_label.grid(row=3, column=0, padx=20, pady=20)
        self.phone_no_entry = tk.Entry(self.frame_register, bg= "beige", fg="brown")
        self.phone_no_entry.grid(row=3, column=1, padx=20, pady=20)

        self.kipande_label = tk.Label(self.frame_register, text= "Your National ID:", bg="beige", fg= "brown")
        self.kipande_label.grid(row=4, column=0, padx=20, pady=20)
        self.kipande_entry = tk.Entry(self.frame_register, bg= "beige", fg="brown")
        self.kipande_entry.grid(row=4, column=1, padx=20, pady=20)

        #button verifies the account number and sends the otp so there will be two uses
        self.butn_reg = tk.Button(self.frame_register, text="Register", fg="brown", bd=0, bg="white", command= self.insert)
        self.butn_reg.grid(row=6, column=0,columnspan=2, pady=10)

    #registering user's face data
    def faces(self, acc):
        self.account = acc 
        print(self.account)
        
        #function for executing face registration
        def insert_face_embedding(cursor, account_number, embedding):
            # Insert the face embedding into the face table along with the account number
            cursor.execute('INSERT INTO face_db (account_number, face_embedding) VALUES (%s, %s)', (account_number, embedding))

        def capture_and_store_faces(cursor, connection, account_number, num_faces):
            # Start the webcam for capturing images
            video_capture = cv2.VideoCapture(0)

            face_count = 0

            while face_count < num_faces:
                # Capture frame-by-frame
                ret, frame = video_capture.read()

                # Convert the image from BGR color (OpenCV default) to RGB color
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Detect faces in the frame
                face_locations = face_recognition.face_locations(rgb_image)

                # If no face is detected, continue to the next frame
                if len(face_locations) == 0:
                    continue
                
                # Encode the detected face images
                face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

                for face_encoding in face_encodings:
                    # Store the face embedding in the database
                    insert_face_embedding(cursor, account_number, np.array(face_encoding))

                    face_count += 1

                # Display the captured image with bounding boxes
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                cv2.imshow('Video', frame)
                cv2.waitKey(1)

            # Release the webcam and close the OpenCV windows
            video_capture.release()
            cv2.destroyAllWindows()
            connection.commit()

        # Example usage
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='52456',
                                     db='mydatabase',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
          # Create the face table if it doesn't exist

            account_number = self.account
            num_faces = 10

            # Capture and store faces in the face database for the specified account number
            capture_and_store_faces(cursor, connection, account_number, num_faces)

        connection.close()

        self.master.destroy()

    #insert user input into database
    def insert(self):
        #name
        name = self.name_entry.get()
        #email
        email= self.email_entry.get()
        #phone
        simu = self.phone_no_entry.get()
        #kipande
        identity = self.kipande_entry.get()
        #account
        prefix = '129098'
        acc = prefix + ''.join(random.choices('0123456789', k=3))
        
        connection = pymysql.connect(host='localhost',
                                user='root',
                                password='52456',
                                db='mydatabase')
            # get some data
        cursor = connection.cursor()
        with connection.cursor() as cursor:
            query = "INSERT INTO bank_users (name, email, phone_number, national_id, account_number) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, email, simu, identity, acc))
        #save the changes
        connection.commit()
        messagebox.showinfo("SUCCESS", f"You have been recorded")
        
        #save faces
        self.account = acc
        self.faces(self.account)

        #destroy previous window
        self.master.destroy()


class HistoryWin():#login
    def __init__(self, master, account):
        self.master = master
        self.account = account
        master.geometry("800x600")
        master.configure(bg="beige")
        master.title("History Payments window")

        # make the window not resizable
        master.resizable(False, True)

        #create a frame and pack but place the labels and entries -------------------------------------
        self. hist = tk.Frame(master, bg= "beige", width=200, height=200)
        self. hist.pack(pady=50)

        self.hist_label = tk.Label(self.hist, text = "Transaction History!", bg = "beige", fg= "brown")
        self.hist_label.pack(padx=20, pady=20)

        # Create a treeview widget to display the transaction history
        self.tree = ttk.Treeview(self.hist, columns=('date', 'type', 'amount'), selectmode='browse')
        self.tree.heading('#0', text='Transaction ID')
        self.tree.heading('date', text='Date')
        self.tree.heading('type', text='Type')
        self.tree.heading('amount', text='Amount')
        self.tree.pack(pady=20)

        # Query the database for transaction history
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     passwd='52456',
                                     database='mydatabase')
        cursor = connection.cursor()
        query = f"SELECT transaction_id, transaction_date, transaction_type, transaction_amount FROM transactions WHERE account_number = '{self.account}'"
        cursor.execute(query)
        results = cursor.fetchall()

        # Populate the treeview with the transaction history
        for row in results:
            self.tree.insert('', 'end', text=row[0], values=(row[1], row[2], row[3]))
 
        self.butn_print = tk.Button(self.hist, text="Print", fg="brown", bd=0, bg="white", command= self.send_transaction_history)
        self.butn_print.pack(padx=30, pady= 30)

    #send the table to user's email
    def send_transaction_history(self):
        # Query the database for transaction history
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     passwd='52456',
                                     database='mydatabase')
        cursor = connection.cursor()

        #get users email based on their account_number
        email = "SELECT email FROM bank_users WHERE account_number = %s"
        cursor.execute(email,(self.account,))
        email_address = cursor.fetchone()
        print(email_address)

        query = f"SELECT transaction_id, transaction_date, transaction_type, transaction_amount FROM transactions WHERE account_number = '{self.account}'"
        cursor.execute(query)
        results = cursor.fetchall()

        # Create a string with the transaction history
        transaction_history = "Transaction history:\n"
        for row in results:
            transaction_history += f"{row[0]} | {row[1]} | {row[2]} | {row[3]} \n"

        # Create a multipart message and set the subject, from, to and attachment
        message = MIMEMultipart()
        message['Subject'] = 'Chase Bank Transaction History'
        message['From'] = 'Nyamburanjenga3482@outlook.com'
        message['To'] = str(email_address)

        # Attach the transaction history table as a text file
        attachment = MIMEText(transaction_history)
        attachment.add_header('Content-Disposition', 'attachment', filename='transaction_history.txt')
        message.attach(attachment)

        # Set up an SMTP connection to the Outlook server and send the email
        with smtplib.SMTP('smtp.office365.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login('Nyamburanjenga3482@outlook.com', 'Uf9LuB9%U(AhbwY')
            smtp.sendmail('Nyamburanjenga3482@outlook.com', email_address, message.as_string())

        # Show a message box to indicate that the email was sent successfully
        messagebox.showinfo("Email Sent", "Transaction history email sent successfully!")
    
        #destroy previous windows
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    my_window = Face_Recog_project(root)
    root.mainloop()

