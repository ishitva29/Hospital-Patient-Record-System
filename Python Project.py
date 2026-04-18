  import csv, os
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PF, BF = "patients.csv", "billing.csv"
patients = []

class Patient:
    def __init__(self, pid, name, age, gender, ward, ad=None, dd=None):
        self.pid, self.name, self.age, self.gender = pid, name, age, gender
        self.ward, self.ad, self.dd = ward, ad, dd

wards = {"General": 5, "ICU": 3, "Private": 2}

def save():
    with open(PF, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ID","Name","Age","Gender","Ward","Admission","Discharge"])
        for p in patients: w.writerow([p.pid,p.name,p.age,p.gender,p.ward,p.ad or "",p.dd or ""])

def load():
    if not os.path.exists(PF): return
    with open(PF) as f:
        for r in csv.DictReader(f):
            patients.append(Patient(r["ID"], r["Name"], int(r["Age"]), r["Gender"], r["Ward"], r["Admission"] or None, r["Discharge"] or None))

def add():
    pid = input("ID: "); 
    if any(p.pid == pid for p in patients): return print("ID exists")
    name = input("Name: "); age = int(input("Age: ")); gender = input("Gender: "); ward = input("Ward(General/ICU/Private): ")
    if age <= 0 or gender.lower() not in ["male","female","other"] or ward not in wards: return print("Invalid input")
    if sum(1 for p in patients if p.ward == ward and not p.dd) >= wards[ward]: return print("Ward full")
    patients.append(Patient(pid, name, age, gender, ward, datetime.now().strftime("%Y-%m-%d")))
    save(); print("Patient added")

def show():
    if not patients: return print("No records")
    print(f"\n{'ID':<8}{'Name':<15}{'Age':<6}{'Gender':<10}{'Ward':<10}{'Adm':<12}{'Dis':<12}")
    for p in patients: print(f"{p.pid:<8}{p.name:<15}{p.age:<6}{p.gender:<10}{p.ward:<10}{str(p.ad):<12}{str(p.dd):<12}")

def search():
    pid = input("Enter ID: ")
    for p in patients:
        if p.pid == pid: return print(vars(p))
    print("Not found")

def update():
    pid = input("Enter ID: ")
    for p in patients:
        if p.pid == pid:
            p.name = input("New name: ") or p.name
            a = input("New age: "); p.age = int(a) if a else p.age
            p.gender = input("New gender: ") or p.gender
            save(); return print("Updated")
    print("Not found")

def delete():
    pid = input("Enter ID: ")
    for p in patients:
        if p.pid == pid: patients.remove(p); save(); return print("Deleted")
    print("Not found")

def discharge():
    pid = input("Enter ID: ")
    for p in patients:
        if p.pid == pid and not p.dd:
            p.dd = datetime.now().strftime("%Y-%m-%d")
            d = max((datetime.strptime(p.dd,"%Y-%m-%d") - datetime.strptime(p.ad,"%Y-%m-%d")).days, 1)
            amt = d * 1000
            with open(BF, "a", newline="") as f:
                w = csv.writer(f)
                if os.stat(BF).st_size == 0: w.writerow(["ID","Amount","Date"])
                w.writerow([pid, amt, p.dd])
            save(); return print(f"Discharged | Bill = ₹{amt}")
    print("Not found / already discharged")

def analytics():
    stays = [max((datetime.strptime(p.dd,"%Y-%m-%d") - datetime.strptime(p.ad,"%Y-%m-%d")).days,1) for p in patients if p.ad and p.dd]
    if stays: print("Avg Stay:", np.mean(stays), "| Max:", np.max(stays), "| Min:", np.min(stays))
    else: print("No discharged data")
    for w in wards:
        occ = sum(1 for p in patients if p.ward == w and not p.dd)
        print(f"{w}: {occ}/{wards[w]} ({occ/wards[w]*100:.1f}%)")

def bill_report():
    if not os.path.exists(BF): return print("No billing file")
    df = pd.read_csv(BF); print(df)
    print("Total:", df["Amount"].sum(), "| Avg:", df["Amount"].mean())

def charts():
    occ = [sum(1 for p in patients if p.ward == w and not p.dd) for w in wards]
    plt.bar(list(wards.keys()), occ); plt.title("Ward Occupancy"); plt.show()
    if os.path.exists(BF):
        df = pd.read_csv(BF)
        if not df.empty:
            plt.figure(); plt.pie(occ, labels=list(wards.keys()), autopct="%1.1f%%"); plt.title("Occupancy Distribution"); plt.show()

load()
while True:
    print("\n1.Add 2.Show 3.Search 4.Update 5.Delete 6.Discharge 7.Analytics 8.Billing 9.Charts 10.Exit")
    try:
        c = int(input("Choice: "))
        if c == 1: add()
        elif c == 2: show()
        elif c == 3: search()
        elif c == 4: update()
        elif c == 5: delete()
        elif c == 6: discharge()
        elif c == 7: analytics()
        elif c == 8: bill_report()
        elif c == 9: charts()
        elif c == 10: break
        else: print("Invalid")
    except Exception as e:
        print("Error:", e)
