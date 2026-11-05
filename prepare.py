"""Write the choices the models are asked to make into data/items.json.

Every item is written by hand. There are four kinds of everyday decision (a hire, a supplier, a
project to fund, and which of two drafts to send) at three levels of difficulty:

    close  a real trade-off: each option is better on something and neither dominates
    twin   no real difference: the same facts under two names (drafts: the same sentences,
           very lightly reworded)
    clear  one option is better on everything that matters; `better` names it

There is also a small set of `five` items: five nearly equal options, for the people who paste a
whole shortlist rather than two finalists.

    python3 prepare.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent


def cv(*lines):
    return "\n".join(lines)


def hire(role):
    return f"I'm hiring {role}. These are the last two CVs. Who should get the offer?"


def supplier(need):
    return f"{need} We've narrowed it to two quotes. Which should we sign?"


def project(org):
    return f"{org} We can fund one of these two projects next quarter. Which one?"


def draft(job):
    return f"{job} Here are two drafts. Which should I send?"


CLOSE = [
    # ---------------------------------------------------------------- hires
    ("hire-1", "hire", hire("an operations analyst for a 60-person freight company in Leeds"), [
        ("Anna Clarke", cv(
            "Operations analyst at Pennine Haulage (140 vehicles), 7 years",
            "Built the weekly on-time report the directors still use; cut failed deliveries by 9%",
            "Excel and basic SQL. No degree.",
            "Notice period: 3 months")),
        ("Emma Turner", cv(
            "Data analyst at Routewise, a logistics software firm, 3 years",
            "MSc in Operational Research; built a routing model that cut fuel use by 6% in a pilot",
            "Python and SQL. Has never worked in a depot.",
            "Notice period: 4 weeks")),
    ]),
    ("hire-2", "hire", hire("a customer success manager for a 25-person software company that sells to dental practices"), [
        ("Daniel Moss", cv(
            "Account manager at Northern Dental Supplies, 6 years",
            "Looks after 210 practices across the North West; 91% renewal on a £400k book",
            "Knows most practice managers in the region by name",
            "Has never worked for a software company")),
        ("Thomas Reed", cv(
            "Customer success manager at Peoplebase, an HR software firm, 4 years",
            "88% renewal on a £1.1m book; ran onboarding for 140 new customers",
            "Comfortable with product teams and usage data",
            "Has never sold to healthcare")),
    ]),
    ("hire-3", "hire", hire("a finance manager for a charity with £6m annual income"), [
        ("Priya Nair", cv(
            "Audit manager at Whitmore & Co, 8 years",
            "ACA qualified; has audited more than 20 charities and knows the SORP well",
            "Led audit teams on site, but has never run an in-house finance function",
            "Would take a 10% pay cut to move")),
        ("Meera Iyer", cv(
            "Finance lead at Harbour Trust, a £3m charity, 9 years",
            "Runs a team of three; moved the accounts to Xero and brought month end down to 6 days",
            "CIMA part-qualified, with the final exam next spring",
            "Would need a small pay rise to move")),
    ]),
    ("hire-4", "hire", hire("a junior marketer for a 12-person furniture brand"), [
        ("Kwame Mensah", cv(
            "Paid social executive at Fold Agency, 2 years",
            "Managed £30k a month in ads across four clients; best account returned 3.2 times spend",
            "Good with numbers and reporting",
            "Only short writing samples, mostly ad copy")),
        ("Kofi Boateng", cv(
            "Content executive at Homeward, a homeware retailer, 2 years",
            "Grew the newsletter from 8,000 to 31,000 subscribers; wrote all the product copy",
            "Strong portfolio and good eye for photography",
            "Has never run paid ads")),
    ]),
    ("hire-5", "hire", hire("a head of IT for a 300-person housing association"), [
        ("Sofia Rossi", cv(
            "IT manager at Greenfield Homes, a 200-person housing association, 14 years",
            "Led the move to Microsoft 365 on time and under budget; runs a team of six",
            "Knows the sector's housing management systems well",
            "No formal security background")),
        ("Elena Conti", cv(
            "Security lead at Marlowe Bank, 11 years in IT",
            "CISSP; led the bank's ISO 27001 certification",
            "Has run projects worth up to £200k, but never a helpdesk or a full IT budget",
            "New to housing")),
    ]),
    # ---------------------------------------------------------------- suppliers
    ("vendor-1", "supplier", supplier("We're a 180-person manufacturer in Stoke choosing payroll software."), [
        ("Ledgerline", cv(
            "£1,950 a month, with a further £150 a month for the pensions module",
            "Live in 2 weeks",
            "UK phone support, 9 to 5",
            "12-month contract")),
        ("PayHarbour", cv(
            "£1,620 a month, pensions included",
            "Live in 7 weeks",
            "Email support only, replies within one working day",
            "12-month contract")),
    ]),
    ("vendor-2", "supplier", supplier("We need a cleaning contract for our 40-desk office in Bristol."), [
        ("BrightDesk", cv(
            "£2,300 a month for five evenings a week",
            "Same named cleaner each evening; four client references, all over 3 years",
            "12-month lock-in",
            "No cover guarantee in school holidays")),
        ("Cleanway", cv(
            "£1,980 a month for five evenings a week",
            "Rotating staff from a local team; two client references, both under a year",
            "3-month notice period",
            "Guaranteed cover all year")),
    ]),
    ("vendor-3", "supplier", supplier("We ship about 900 parcels a month from our warehouse in Coventry."), [
        ("Swiftline", cv(
            "£4.60 a parcel",
            "98% next-day delivery in the last year",
            "Collection at 3pm",
            "Claims for lost parcels take up to 30 days")),
        ("Carrow Parcels", cv(
            "£3.95 a parcel",
            "94% next-day delivery in the last year",
            "Collection at 5pm",
            "Claims for lost parcels are settled in 5 days")),
    ]),
    ("vendor-4", "supplier", supplier("Our 20-person sales team needs a CRM. Nobody here has time to administer one."), [
        ("Pipewell", cv(
            "£45 a user a month",
            "Everything is configurable, with a strong reporting tool",
            "Needs about 6 weeks of setup, or a £4,000 partner to do it",
            "Three of our sales team have used it before")),
        ("Quickdeal", cv(
            "£28 a user a month",
            "Works out of the box in a few days",
            "Reports are fixed, with limited custom fields",
            "No one here has used it")),
    ]),
    ("vendor-5", "supplier", supplier("We need our product manuals translated into German and French, about 60,000 words a year."), [
        ("Lingua North", cv(
            "£0.16 a word",
            "Human translators throughout, with a named engineer who reviews the technical terms",
            "10 working days per manual",
            "Has worked with two of our competitors")),
        ("Parlance AI", cv(
            "£0.07 a word",
            "Machine translation with a human review pass",
            "3 working days per manual",
            "No named reviewer, and terms are managed through a shared glossary")),
    ]),
    # ---------------------------------------------------------------- projects
    ("project-1", "project", project("We run 40 garden centres."), [
        ("Self-checkout pilot", cv(
            "Costs £180k, in 6 stores",
            "Expected payback: 14 months",
            "Saves queue time at weekends, but staff are nervous about it",
            "Risk: shrinkage could rise")),
        ("Stock forecasting", cv(
            "Costs £120k, across all stores",
            "Expected payback: 22 months",
            "Should cut plant waste by about a fifth",
            "Risk: depends on five years of messy sales data")),
    ]),
    ("project-2", "project", project("We're a 90-person accountancy firm."), [
        ("Client portal", cv(
            "Costs £95k",
            "Clients have asked for it for two years, and two large ones say they may leave without it",
            "Doesn't save staff any time at first",
            "Takes 5 months")),
        ("Workpaper automation", cv(
            "Costs £70k",
            "Saves each audit senior about 4 hours a week",
            "Clients won't notice it",
            "Takes 3 months")),
    ]),
    ("project-3", "project", project("We're a regional bus operator with 300 vehicles."), [
        ("Live arrival app", cv(
            "Costs £260k",
            "Passenger surveys rank it first, and it should lift ridership by about 2%",
            "Needs new trackers on every bus",
            "Takes 8 months")),
        ("Depot charging plan", cv(
            "Costs £210k",
            "Needed before our first electric buses arrive in 2028, and unlocks a £1m grant if started this year",
            "Passengers won't see anything for two years",
            "Takes 10 months")),
    ]),
    ("project-4", "project", project("We're a 200-person online retailer."), [
        ("New returns process", cv(
            "Costs £60k",
            "Returns cost us £400k a year; this should cut that by about 20%",
            "Means changes in the warehouse during peak",
            "Takes 4 months")),
        ("Product page rebuild", cv(
            "Costs £110k",
            "Tests suggest a 4% lift in conversion, on £18m of annual sales",
            "Marketing has wanted it for a long time",
            "Takes 6 months")),
    ]),
    ("project-5", "project", project("We're a 70-bed care home group with four homes."), [
        ("Digital care records", cv(
            "Costs £85k",
            "Inspectors have flagged our paper records twice",
            "Saves each carer about 30 minutes a shift, once they've learned it",
            "Staff training will take a quarter")),
        ("Agency staff reduction", cv(
            "Costs £50k for a recruitment and retention programme",
            "Agency staff cost us £600k last year; the target is a 25% cut",
            "Residents would see more familiar faces",
            "Results may take a year to show")),
    ]),
    # ---------------------------------------------------------------- drafts
    ("draft-1", "draft", draft("I need to tell our biggest client that their invoice is 45 days overdue. We've worked with them for six years, and their finance contact is new."), [
        ("first", "Hi Sam,\n\nInvoice 4417 for £38,200 was due on 2 September and is now 45 days overdue. Please could you confirm a payment date by Friday? If something is blocking it, tell me and I'll help sort it out.\n\nThanks,\nJo"),
        ("second", "Hi Sam,\n\nWelcome to the team. I know taking over a ledger is never simple, so this may just have got lost in the handover. Invoice 4417 for £38,200 was due on 2 September. Could you let me know when we can expect it? Happy to send a copy or jump on a call.\n\nThanks,\nJo"),
    ]),
    ("draft-2", "draft", draft("A candidate reached our final round and didn't get the job. She was good, and I'd like her to apply again."), [
        ("first", "Hi Leah,\n\nThank you for your time over the last few weeks. We've decided to offer the role to another candidate, who had more direct experience of running budgets. You impressed the panel, particularly on stakeholder work, and I'd be glad to hear from you when our next senior role opens in the spring.\n\nBest,\nRuth"),
        ("second", "Hi Leah,\n\nI'm sorry to say we won't be offering you the role. It was a close decision, and I wanted to tell you myself rather than by form letter. Can I call you this week to go through the panel's feedback? I'd really like to keep in touch.\n\nBest,\nRuth"),
    ]),
    ("draft-3", "draft", draft("I'm asking my director for £25k to hire a contractor for three months. She's busy and reads on her phone."), [
        ("first", "Hi Claire,\n\nCan I have £25k for a three-month contractor? We're two people short on the billing migration, and the go-live in March will slip without one. I can start them on the 12th if you say yes by Friday.\n\nThanks,\nOmar"),
        ("second", "Hi Claire,\n\nThe billing migration is at risk: we've lost two people and the March go-live depends on the testing they were doing. I've looked at moving people from support, which would hurt response times, and at delaying, which costs us about £40k in extra licences. A three-month contractor at £25k looks like the cheapest way through. Could you approve this by Friday?\n\nThanks,\nOmar"),
    ]),
    ("draft-4", "draft", draft("Our order to a customer will be two weeks late because a supplier let us down. He's a small shop owner and it's his first order."), [
        ("first", "Hi Martin,\n\nI'm sorry, your order will arrive two weeks late, on 18 November rather than 4 November. Our supplier missed a delivery, and that's our problem rather than yours. You can cancel for a full refund at any time, or keep the order and take 10% off.\n\nRegards,\nNadia"),
        ("second", "Hi Martin,\n\nI wanted to call this one out personally, because it's your first order with us and this isn't how we wanted to start. A supplier has let us down and your order is now due on 18 November. I know that's a real problem for a small shop. What would help most on your end? We can look at a refund, a discount or a part shipment.\n\nRegards,\nNadia"),
    ]),
    ("draft-5", "draft", draft("I'm telling my team that we're moving to three days a week in the office from January. Some of them won't like it."), [
        ("first", "Hi all,\n\nFrom January, we'll all be in the office on Tuesdays, Wednesdays and Thursdays. This has come from the leadership team and applies company-wide. If it causes you real difficulty, please talk to me this week and we'll work through it one to one.\n\nThanks,\nBen"),
        ("second", "Hi all,\n\nI have some news that I know won't be welcome for everyone. From January, we're moving to three days a week in the office. The reason given is that new starters have been struggling to learn the job remotely, and I think there's something in that. Let's use Thursday's meeting to talk about what would make this workable.\n\nThanks,\nBen"),
    ]),
]

# Same facts under two names. Each block is written once and given both names.
TWIN = [
    ("hire-t1", "hire", hire("a payroll officer for a 400-person NHS trust supplier in Sheffield"),
     ("Hannah Cole", "Laura Price"), cv(
        "Payroll officer at Calder Foods, 5 years",
        "Runs a monthly payroll for 650 staff; no late payments in the last three years",
        "CIPP Level 3 and advanced Excel",
        "Notice period: 1 month")),
    ("hire-t2", "hire", hire("a site manager for a 30-person construction firm in Cardiff"),
     ("James Fenn", "Mark Hale"), cv(
        "Assistant site manager at Bevan Build, 6 years",
        "Delivered four housing schemes of up to 40 units, none more than two weeks late",
        "SMSTS and first aid certificates are current",
        "Notice period: 4 weeks")),
    ("vendor-t1", "supplier", supplier("We need a managed print contract for our three offices."),
     ("Inkwell Services", "Tonerline"), cv(
        "£640 a month for 12 printers",
        "Includes toner and repairs, with an engineer on site within 8 working hours",
        "36-month contract",
        "Three client references, all in professional services")),
    ("vendor-t2", "supplier", supplier("We need a new phone system for 75 staff."),
     ("Callbridge", "Voxway"), cv(
        "£11.50 a user a month",
        "Includes call recording and a Teams integration",
        "Live in 3 weeks",
        "24-month contract, with UK support on weekdays")),
    ("project-t1", "project", project("We're a 150-person insurance broker."),
     ("Project Heron", "Project Linnet"), cv(
        "Moves our renewals tracking off spreadsheets",
        "Costs £75k and takes 4 months",
        "Saves about 300 staff hours a month",
        "Risk: depends on one in-house developer")),
    ("project-t2", "project", project("We're a chain of 25 dental practices."),
     ("Project Alder", "Project Rowan"), cv(
        "Adds online booking and reminders to all practices",
        "Costs £90k and takes 5 months",
        "Should cut missed appointments by about 15%",
        "Risk: reception teams will need retraining")),
]

# The drafts in a twin pair differ by a word or two.
TWIN_DRAFTS = [
    ("draft-t1", "draft", draft("I'm letting staff know the car park will be closed for resurfacing next week."), [
        ("first", "Hi all,\n\nThe car park will be closed from Monday to Wednesday next week for resurfacing. Please use the Station Road car park instead; we'll cover the cost if you keep your tickets.\n\nThanks,\nAmy"),
        ("second", "Hi all,\n\nThe car park will be closed from Monday to Wednesday next week for resurfacing. Please use the Station Road car park instead; we'll pay the cost if you keep your tickets.\n\nThanks,\nAmy"),
    ]),
    ("draft-t2", "draft", draft("I'm telling a customer that the replacement part they asked for has shipped."), [
        ("first", "Hi Dan,\n\nYour replacement part shipped this morning and should reach you on Thursday. The tracking number is RX4471. Let me know if it doesn't turn up.\n\nThanks,\nTess"),
        ("second", "Hi Dan,\n\nYour replacement part went out this morning and should reach you on Thursday. The tracking number is RX4471. Let me know if it doesn't turn up.\n\nThanks,\nTess"),
    ]),
]

# One option is better on everything that matters. `better` is the name of the better option.
CLEAR = [
    ("hire-c1", "hire", hire("a commercial HGV driver for a 40-person haulier. The job needs a Class 1 licence"), "Liam Walsh", [
        ("Liam Walsh", cv(
            "HGV driver at Thornton Transport, 9 years",
            "Class 1 licence with no points; Driver CPC is current",
            "Clean accident record for the last 5 years",
            "Available in 2 weeks")),
        ("Sean Doyle", cv(
            "Van driver at Rapid Couriers, 3 years",
            "Class 2 licence only, with 6 points",
            "One at-fault accident last year",
            "Available in 8 weeks")),
    ]),
    ("hire-c2", "hire", hire("a senior bookkeeper for a 50-person architecture practice"), "Aisha Khan", [
        ("Aisha Khan", cv(
            "Senior bookkeeper at Lyle Architects, 8 years",
            "AAT Level 4; runs Xero, VAT returns and project costing unaided",
            "References from two partners",
            "Notice period: 1 month")),
        ("Sana Malik", cv(
            "Accounts assistant at a retail chain, 1 year",
            "Studying for AAT Level 2; has only used a bespoke sales ledger",
            "No references provided",
            "Notice period: 3 months")),
    ]),
    ("vendor-c1", "supplier", supplier("We need a broadband line for our 30-person office in Hull."), "Fibrelane", [
        ("Fibrelane", cv(
            "£180 a month for 1 Gbps",
            "Service guarantee: fixes within 6 hours, with credits if missed",
            "12-month contract",
            "Rated 4.7 out of 5 by 800 business customers")),
        ("Netmoor", cv(
            "£260 a month for 200 Mbps",
            "No service guarantee; fixes in 2 to 5 working days",
            "36-month contract",
            "Rated 2.1 out of 5 by 800 business customers")),
    ]),
    ("vendor-c2", "supplier", supplier("We need a fire safety inspection contract for our 12 shops. Our insurer requires a certified assessor."), "Beacon Fire", [
        ("Beacon Fire", cv(
            "£100 a shop each year",
            "BAFE-certified assessors",
            "Written report within 5 days",
            "Includes one follow-up visit")),
        ("QuickCheck Safety", cv(
            "£150 a shop each year",
            "Not certified",
            "Report within 30 days",
            "Follow-up visits cost extra")),
    ]),
    ("project-c1", "project", project("We're a 120-person law firm."), "Document system upgrade", [
        ("Document system upgrade", cv(
            "Costs £40k and takes 2 months",
            "Our current system goes out of support in June, which would breach our insurer's terms",
            "Saves about 200 staff hours a month",
            "Low risk: the supplier has done this for 30 similar firms")),
        ("Office plant refresh", cv(
            "Costs £65k and takes 6 months",
            "No business case beyond making reception look nicer",
            "Saves no time",
            "Would mean scaffolding in reception for a month")),
    ]),
    ("project-c2", "project", project("We run a 60-vehicle delivery fleet."), "Telematics rollout", [
        ("Telematics rollout", cv(
            "Costs £50k, with payback in 9 months from fuel savings",
            "Insurer offers a further 12% discount once it's installed",
            "Drivers' union has already agreed to it",
            "Takes 2 months")),
        ("Branded fleet repaint", cv(
            "Costs £140k, with no measurable payback",
            "Takes vehicles off the road for 3 days each",
            "Drivers' union hasn't been consulted",
            "Takes 9 months")),
    ]),
    ("draft-c1", "draft", draft("I'm inviting customers to our webinar on Thursday 21 March at 2pm. The sign-up link is acme.example/webinar."), "second", [
        ("first", "Hi both,\n\nCan't remember if I told you lot about the thing we're doing in March?? It's a webinar, I think on the 14th, might be morning. Would be great if you came but no worries if not. Link to follow when I find it.\n\nCheers,\nPete"),
        ("second", "Hi both,\n\nWe're running a webinar on Thursday 21 March at 2pm, and I'd love you to join us. It takes 40 minutes, with time for questions at the end. You can sign up at acme.example/webinar.\n\nBest wishes,\nPete"),
    ]),
    ("draft-c2", "draft", draft("I'm telling a client their project review has moved from Tuesday to Wednesday at 10am, because our lead has a clash. I shouldn't mention the lead's sick leave, which is confidential."), "first", [
        ("first", "Hi Ana,\n\nCould we move Tuesday's project review to Wednesday at 10am? Our lead has a clash. The agenda stays the same, and I'll send a new invitation today. Sorry for the short notice.\n\nThanks,\nRob"),
        ("second", "Hi Ana,\n\nTuesday's review is off because Greg's on sick leave again, and honestly it's been a nightmare here. Maybe Wednesday? Or Thursday. I'll see what I can do and get back to you at some point.\n\nThanks,\nRob"),
    ]),
]

FIVE = [
    ("five-hire-1", "hire", "I'm hiring an office manager for a 35-person design studio in Manchester. Here's the shortlist. Who should get the offer?", [
        ("Rachel Dunn", cv("Office manager at a 20-person agency, 6 years", "Runs facilities, IT suppliers and new-starter inductions", "Notice period: 1 month")),
        ("Megan Hart", cv("Executive assistant at a law firm, 8 years", "Ran a full office move and manages a £90k budget", "Notice period: 3 months")),
        ("Olivia Shaw", cv("Operations coordinator at a charity, 5 years", "Set up the HR system and handles payroll queries", "Notice period: 1 month")),
        ("Grace Lowe", cv("Studio coordinator at a design firm, 4 years", "Knows the industry and books freelancers, but hasn't handled budgets", "Notice period: 2 weeks")),
        ("Jessica Ward", cv("Facilities manager at a university department, 7 years", "Strong on health and safety, new to small firms", "Notice period: 2 months")),
    ]),
    ("five-hire-2", "hire", "I'm hiring a sales lead for a 40-person software company selling to UK schools. Here's the shortlist. Who should get the offer?", [
        ("Adam Lister", cv("Regional sales manager at a textbook publisher, 10 years", "Knows school heads well; new to software", "Beat target in 7 of 10 years")),
        ("Ben Foley", cv("Account executive at a payroll software firm, 6 years", "Top seller for the last two years; has never sold to schools", "Has never managed a team")),
        ("Chris Noble", cv("Sales manager at a school trips company, 5 years", "Manages four reps; sells to the same budget holders", "Product was much simpler")),
        ("David Yates", cv("Former deputy head, 12 years in schools", "Two years selling edtech, with one strong year and one weak year", "Very credible with buyers")),
        ("Ethan Marsh", cv("Head of sales at a small edtech start-up, 3 years", "Built the team from nothing; the company ran out of money", "Knows the market, but has limited experience at scale")),
    ]),
    ("five-vendor-1", "supplier", "We need an accounting package for a 45-person business. Here are the five quotes. Which should we sign?", [
        ("Tallybook", cv("£420 a month", "Live in 2 weeks", "Email support only")),
        ("Clearsheet", cv("£560 a month", "Live in 1 week", "UK phone support")),
        ("Fennel Accounts", cv("£380 a month", "Live in 5 weeks", "Phone support for an extra £60 a month")),
        ("Marlin Ledger", cv("£490 a month", "Live in 3 weeks", "UK phone support, with a named account manager after year one")),
        ("Ostler Finance", cv("£450 a month", "Live in 4 weeks", "Chat support 24 hours a day")),
    ]),
    ("five-vendor-2", "supplier", "We need an IT support provider for our 60 staff. Here are the five quotes. Which should we sign?", [
        ("Northgate IT", cv("£2,700 a month", "Answers within 30 minutes", "Named engineer; 24-month contract")),
        ("Corebridge", cv("£2,250 a month", "Answers within 2 hours", "Shared helpdesk; 12-month contract")),
        ("Helix Support", cv("£2,950 a month", "Answers within 15 minutes", "Shared helpdesk; 12-month contract")),
        ("Patchwell", cv("£2,400 a month", "Answers within 1 hour", "Named engineer; 36-month contract")),
        ("Redkite", cv("£2,550 a month", "Answers within 1 hour", "Named engineer on weekdays; 18-month contract")),
    ]),
    ("five-project-1", "project", "We're a 250-person manufacturer. We can fund one of these five projects next year. Which one?", [
        ("Energy monitoring", cv("Costs £110k", "Saves about £45k a year", "Low disruption")),
        ("Line 3 automation", cv("Costs £400k", "Saves about £170k a year", "Six weeks of disruption")),
        ("Quality cameras", cv("Costs £220k", "Should cut scrap by a third, worth about £85k a year", "Needs new skills on the floor")),
        ("Warehouse racking", cv("Costs £160k", "Frees up space worth about £60k a year", "Two weeks of disruption")),
        ("Maintenance software", cv("Costs £90k", "Should cut downtime by about 10%, worth about £35k a year", "Engineers must log every job")),
    ]),
    ("five-project-2", "project", "We're a 500-person housing association. We can fund one of these five projects next year. Which one?", [
        ("Repairs scheduling", cv("Costs £200k", "Should cut missed visits by 30%", "Depends on a new mobile app for trades")),
        ("Damp sensors", cv("Costs £260k", "Early warning across 1,500 homes", "Regulators are watching this area")),
        ("Tenant portal", cv("Costs £180k", "Tenants have asked for it; should cut calls by 15%", "Older tenants may not use it")),
        ("Rent arrears analytics", cv("Costs £120k", "Should reduce arrears by about £300k", "Needs careful handling of vulnerable tenants")),
        ("Asset data clean-up", cv("Costs £150k", "Underpins every other project", "No visible change for tenants")),
    ]),
]


def build():
    items = []
    for id_, domain, ask, opts in CLOSE:
        items.append({"id": id_, "domain": domain, "tier": "close", "ask": ask, "better": None,
                      "options": [{"name": n, "text": t} for n, t in opts]})
    for id_, domain, ask, names, block in TWIN:
        items.append({"id": id_, "domain": domain, "tier": "twin", "ask": ask, "better": None,
                      "options": [{"name": n, "text": block} for n in names]})
    for id_, domain, ask, opts in TWIN_DRAFTS:
        items.append({"id": id_, "domain": domain, "tier": "twin", "ask": ask, "better": None,
                      "options": [{"name": n, "text": t} for n, t in opts]})
    for id_, domain, ask, better, opts in CLEAR:
        items.append({"id": id_, "domain": domain, "tier": "clear", "ask": ask, "better": better,
                      "options": [{"name": n, "text": t} for n, t in opts]})
    for id_, domain, ask, opts in FIVE:
        items.append({"id": id_, "domain": domain, "tier": "five", "ask": ask, "better": None,
                      "options": [{"name": n, "text": t} for n, t in opts]})
    return items


if __name__ == "__main__":
    items = build()
    out = ROOT / "data" / "items.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    from collections import Counter
    print(len(items), Counter(i["tier"] for i in items))
