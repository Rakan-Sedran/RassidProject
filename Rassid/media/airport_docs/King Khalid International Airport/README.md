# Rassid — Flight Tracking Platform

## Project Description
Rassid is a platform designed to enhance the passenger travel experience by providing accurate and real‑time flight information.  
It delivers complete details for passengers from the moment a flight arrives at the airport until departure, including gate updates, boarding times, and instant notifications.

## Problem
Passengers face several issues at airports:
- No unified platform showing gate information and its location.
- Gate changes occur without prior notice.
- Passengers must frequently check airport screens manually.
- Time is wasted searching for the latest updates.
- Difficulty locating the gate inside the airport.

## Solution
Rassid provides a unified system that includes:
- Public flight listings for every airport.
- Private tracking links for passengers.
- Tools for airports to add gate and boarding information.
- Instant SMS/Email notifications for any updates.
- A simple map showing the gate location inside the airport.

## Key Features
- Public access to flight listings without login.
- Private and accurate tracking for each passenger.
- SMS & Email alerts for updates.
- Gate map & navigation.
- Full airport staff management tools.

---

# User Stories

## Passenger

### 1. Private Tracking Link
When opening the tracking link, the passenger sees:
- Basic flight info: Flight Number, Origin, Destination  
- Departure & arrival times  
- Flight status (On Time / Delayed / Boarding / Cancelled)  
- Current gate  
- Terminal  
- Countdown timer  
- Latest updates (gate change, boarding started…)  
- Last update timestamp  
- Refresh button

Behavior:
- Works without login  
- Unique for each passenger  
- Updates displayed instantly  

### 2. Gate Change Notifications
Passenger receives:
- SMS + Email  
- Includes:
  - New gate  
  - Time of change  
  - Tracking link  

### 3. Boarding Times
Shows:
- Boarding Opens  
- Boarding Closes  
- Countdown timer  

### 4. Gate Map
- 2D placeholder map  
- Gate pin  
- “Get Directions” button  

### 5. Browse Airports & Flights
- List of airports (RUH, JED, DMM…)  
- View Arrivals / Departures  
- Public flight details (no private data)

---

## Airport Operator

### 1. View API Flights
Flight table:
- Flight Number, Origin, Destination, Time, Status  
- Filters  
- Edit buttons  

### 2. Add Gate & Boarding Info
Edit page fields:
- Gate Code  
- Terminal  
- Boarding Open  
- Boarding Close  
- Notes  
- Save → updates DB + triggers notifications  

### 3. Modify Gate or Flight Status
Possible actions:
- Change gate  
- Update boarding times  
- Reschedule  
- Delay flight  
- Close gate  

System automatically:
- Logs change in `FlightStatusHistory`  
- Sends SMS/Email  
- Updates passenger pages  

### 4. View Passengers of a Flight
Table:
- Name, Email, Phone  
- Notification status  
- Resend button  

### 5. Upload CSV
- Upload file  
- Download template  
- Preview  
- Confirm upload  
- Tracking links generated  

### 6. Create Ticket to Airport Admin
Fields:
- Title  
- Category  
- Description  
- Priority  
- Submit  

---

## Airport Admin

### 1. Manage Employees
- Add/Edit/Delete employees  
- Assign roles (admin/operator)  
- Link to airport  
- Activate/Deactivate  

### 2. Flight Reports
Includes:
- Number of flights today  
- Number of updates made  
- Avg gate update time  
- Notification success rate  
- Most changing flights  

### 3. Notification Insights
- Delivery Rate chart  
- Failed Notifications chart  
- Last 50 notifications  

### 4. Create Ticket to Platform Admin
- Same ticket form as operator  
- Status: Pending, In Progress, Resolved  

### 5. Approve/Reject Operator Tickets
- Accept → escalate  
- Reject → close  
- Add note  

### 6. View Airport Subscription
- Plan  
- Expiry date  
- Max employees  
- Renew button  
- Payment history  

---

## Platform Super Admin

### 1. View All Airports
Table:  
- Airport name  
- Country  
- Subscription status  
- Employee count  
- View button  

### 2. Manage Subscriptions
- Renew  
- Modify  
- Pause  
- Cancel  
- Send invoice  

### 3. Global Dashboard
- Total airports  
- Total employees  
- Total passengers today  
- Total notifications sent  
- Delivery rate  
- Updated flights count  
- Alerts (API/SMS issues)  

### 4. Manage Airport Admins
- List  
- Add  
- Reset password  
- Disable  

### 5. Ticket System
- View tickets  
- Assign  
- Change status  
- Reply  
- Close  

### 6. System Errors
- API errors  
- SMS provider errors  
- Failed emails  
- System logs

---

## Wireframe
- Home <img width="2816" height="1369" alt="Screenshot_2025-12-16_093418" src="https://github.com/user-attachments/assets/45dbc632-4113-40d4-adc2-2f9b6c3d867c" />
- About Us <img width="1411" height="1381" alt="Screenshot_2025-12-16_093448" src="https://github.com/user-attachments/assets/5e9d5c10-2e22-406c-bfc0-2ddcae6a20e7" />
- Passenger Tracking <img width="1014" height="1427" alt="Screenshot_2025-12-16_093515" src="https://github.com/user-attachments/assets/31f154d3-e3d2-4f7b-a8b2-264b11839b91" />
- Soper Admin Dashboard <img width="1179" height="1462" alt="Screenshot_2025-12-16_093634" src="https://github.com/user-attachments/assets/cf2e7a84-a70d-4f51-8d6a-ae8233c15baa" />
- Admin Dashboard  <img width="999" height="1414" alt="Screenshot_2025-12-16_093606" src="https://github.com/user-attachments/assets/e64cb317-3525-40a5-b6d2-5dcdb012ae52" />
- Operator Dashboard <img width="1569" height="918" alt="Screenshot_2025-12-16_093540" src="https://github.com/user-attachments/assets/48617c6e-33ca-4338-a7da-24904ff6ee18" />

---

## UML
- Classes <img width="1190" height="1131" alt="ZLNRZjis47tNLmZxs29nyce4RjnjsXfejulQ_O0nEPQ9vOKOZhph5lttoc9M5YzkzaqwdCiPyl3mSs0WxerkmfEo7WXCApI4i6OcjUyPDyBPhVeRsmzDCwwqFslL7RdzfsdRxvLSjihovVCmmW-zsICjsy2aR7V10mFt8K744MMlKVw4_jATSDbAO6HbC5bV4waJw7GL56bbyTv9d8f6s3lYp" src="https://github.com/user-attachments/assets/aad63839-56fb-4288-8db6-2f0ac8489ada" />

- Use Case<img width="970" height="1982" alt="IMG_3587" src="https://github.com/user-attachments/assets/ad7f35cf-ba33-4753-8cb0-3e105b264c3f" />
- Sequence <img width="970" height="1204" alt="IMG_3585" src="https://github.com/user-attachments/assets/aa04b7fd-7524-45bf-b260-53051e2770ef" />


# Team Members

- Nawaf Alburaykan
- Rakan Alyami
- Abdulrahman Alqahtani
- Ziyad Alzahrani

**Supervisor:** Mr. Aqeel Alaid