# https://beta.openai.com/playground/p/bgFErKOAwhe5j9o7w3jI3Ynz?model=davinci-instruct-beta

EDIT_EMAIL_DATASET_TRAIN = """
Revise the first draft email based on user feedback

INPUT
Send an email to mission@bodyrok.com. Ask to pause membership starting this Thursday and resume in October. Explain my reason is I'm leaving for an RV trip for 1-2 months.

FIRST DRAFT
Hello Bodyrok Mission,
Is it possible to pause my membership starting Thursday? And resume the membership in October. I'm leaving for an RV trip for 1-2 months and won't be back until October. Thanks!
Brendan

FEEDBACK
Replace Bodyrok Mission with team. Change Thursday to Friday the 14th. Change the signature to Thanks, Brendan

REVISED EMAIL
Hello team,
Is it possible to pause my membership starting Friday the 14th? And resume the membership in October. I'm leaving for an RV trip for 1-2 months and won't be back until October. Thanks!
Thanks,
Brendan
<<END>>

INPUT
Reply to Colin and let him know I'm coming to Alaska. I've thought it over and decided it seems fun. Tell him I'll start looking for flights. And ask when he's flying out.

FIRST DRAFT
Hi Colin Fortuner,
I wanted to let you know I've decided to come to Alaska! It seems fun. I'll start looking for flights know. Could you let me know when your flight is?

FEEDBACK
Replace Colin Fortuner with Cols. Add hope you're well at the beginning. Add From, Brendan.

REVISED EMAIL
Hi Cols,
Hope you're well! I wanted to let you know I've decided to come to Alaska! It seems fun. I'll start looking for flights know. Could you let me know when your flight is?
From, Brendan
<<END>>

INPUT
Email Bill Fortuner. Ask if he has the tennis tickets and whether he'd like me to pay. If so, how much. Which payment method. I'm looking forward to getting together! 

FIRST DRAFT
Hey Dad,
Did you get the tennis tickets? Let me know if you want me to pay! If you do, let me know how much and how I can pay you. Venmo?
Brendan

FEEDBACK
Replace Hey Bill with Dad. Add Paypal as a payment option.

REVISED EMAIL
Dad,
Did you get the tennis tickets? Let me know if you want me to pay! If you do, let me know how much and how I can pay you. Venmo or Paypal?
Brendan
<<END>>

INPUT
Reply to Lumen Support and paste my fedex tracking number 175452902. Let them know I filled out the form. Ask when I'll get the refund.

FIRST DRAFT
Hi Lumen Support,
I filled out the form. When will I get the refund?
Brendan

FEEBACK
Add my fedex tracking number. Change the intro to Hi team. Add Are you open today? to the beginning.

REVISED EMAIL
Hi team,
Are you open today? I filled out the form. When will I get the refund?
My fedex tracking number is 175452902.
Brendan
<<END>>

INPUT
Email my manager Xin and let know know I've decided to leave Cruise. Flexible on when I leave. It's up to him. I'd like to stick around at least until October 15 when my vest day is.

FIRST DRAFT
Hi Xin,
I've decided to leave Cruise. I'm flexible on when I leave. It's up to you. I would like to stick around until October 15 when my vest day is.

FEEDBACK
Remove Hi Xin. Change October 15 to November 15

REVISED EMAIL
I've decided to leave Cruise. I'm flexible on when I leave. It's up to you. I would like to stick around until November 15 when my vest day is.
<<END>>
"""