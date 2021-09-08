# Prompt: https://beta.openai.com/playground/p/MOuS7ocSyR4KEhjtlGb6rbMq?model=davinci-instruct-beta

COMPOSE_EMAIL_DATASET_TRAIN = """

Help Brendan compose emails from the following notes

INPUT
Send an email to mission@bodyrok.com. Ask to pause membership starting this Thursday and resume in October. Explain my reason is I'm leaving for an RV trip for 1-2 months.

EMAIL
to: mission@bodyrok.com
subject: Pause membership
body:
Hello,
Is it possible to pause my membership starting Thursday? And resume the membership in October. I'm leaving for an RV trip for 1-2 months and won't be back until October. Thanks!
Brendan
<<END>>

INPUT
Reply to Colin and let him know I'm coming to Alaska. I've thought it over and decided it seems fun. Tell him I'll start looking for flights. And ask when he's flying out.

EMAIL
to: Colin
subject: Alaska trip
body:
I wanted to let you know I've decided to come to Alaska! It seems fun. I'll start looking for flights know. Could you let me know when your flight is?
<<END>>

INPUT
Email Bill Fortuner. Ask if he has the tennis tickets and whether he'd like me to pay. If so, how much. Which payment method. I'm looking forward to getting together! 

EMAIL
to: Bill Fortuner
subject: Tennis tickets payment
body:
Hey Bill,
Did you get the tennis tickets? Let me know if you want me to pay! If you do, let me know how much and how I can pay you. Venmo?
Brendan
<<END>>

INPUT
Email my manager Xin and let know know I've decided to leave Cruise. Flexible on when I leave. It's up to him. I'd like to stick around at least until October 15 when my vest day is.

EMAIL
to: Xin
subject: Leaving Cruise
body:
Hi Xin,
I've decided to leave Cruise. I'm flexible on when I leave. It's up to you. I would like to stick around until October 15 when my vest day is.
Brendan
<<END>>

INPUT
Reply to Lumen Support and paste my fedex tracking number 175452902. Let them know I filled out the form. Ask when I'll get the refund.

EMAIL
to: Lumen Support
subject: Lumen refund
body:
Hi Lumen Support,
I filled out the form and attached my Fedex tracking number 175452902. When will I get the refund?
Brendan

"""