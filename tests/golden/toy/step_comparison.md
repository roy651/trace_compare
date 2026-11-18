## Comparison 1

### Task: Book the cheapest flight from Boston to Denver on 3 May for one adult.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book the cheapest Boston to Denver flight on 3 May for one adult

Failed trace: Book cheapest flight Boston to Denver, 3 May, one adult

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['flights', 'payments']

Failed trace: ['flights', 'payments']

Comparison mode: exact_match
Fields are similar


Comparison field: steps

Successful trace: [{'action': 'search flights', 'app': 'flights'}, {'action': 'book flight', 'app': 'flights'}, {'action': 'charge card', 'app': 'payments'}]

Failed trace: [{'action': 'search flights', 'app': 'flights'}, {'action': 'book flight', 'app': 'flights'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
Fields are similar


Comparison field: steps[].app

Successful trace: ['flights', 'flights', 'payments']

Failed trace: ['flights', 'flights', 'payments']

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['flights.search', 'flights.book', 'payments.charge']

Failed trace: ['flights.search', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: ToolSelector
Different fields: selected_tools

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: flights.search

Failed trace: flights.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: flights.book

Failed trace: flights.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 5

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: payments.charge

Failed trace: payments.charge

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 6

Successful trace: Verifier

Failed trace: Verifier


Comparison field: status

Successful trace: ok

Failed trace: failed

Comparison mode: exact_match
**Fields are different**


Comparison field: amount

Successful trace: 212.4

Failed trace: 212.4

Comparison mode: approximate_numeric
Fields are similar


Comparison field: issues

Successful trace: None

Failed trace: ['card charged but no booking reference']

Comparison mode: field_exists
**Fields are different**

**Step outputs are different**

### Step 7

Successful trace: Responder

Failed trace: Responder


Comparison field: answer

Successful trace: Booked UA 1432 from Boston to Denver on 3 May for 212.40 USD.

Failed trace: I charged 212.40 USD but could not confirm a booking for UA 1432.

Comparison mode: fuzzy_match
**Fields are different**

**Step outputs are different**

**Both traces completed**


## Comparison 2

### Task: Book a flight from London to Tokyo on 20 September.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book a flight from London to Tokyo on 20 September

Failed trace: Book a flight London to Tokyo on 20 September

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['flights', 'payments']

Failed trace: ['flights', 'payments']

Comparison mode: exact_match
Fields are similar


Comparison field: steps

Successful trace: [{'action': 'search flights', 'app': 'flights'}, {'action': 'book flight', 'app': 'flights'}, {'action': 'charge card', 'app': 'payments'}]

Failed trace: [{'action': 'search flights', 'app': 'flights'}, {'action': 'book flight', 'app': 'flights'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
Fields are similar


Comparison field: steps[].app

Successful trace: ['flights', 'flights', 'payments']

Failed trace: ['flights', 'flights', 'payments']

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['flights.search', 'flights.book', 'payments.charge']

Failed trace: ['flights.search', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: ToolSelector
Different fields: selected_tools

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: flights.search

Failed trace: flights.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: flights.book

Failed trace: flights.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**Final divergence: Failed trace completed**


## Comparison 3

### Task: Find a flight from Seattle to San Francisco on 9 July and book it.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Find a flight from Seattle to San Francisco on 9 July and book it

Failed trace: Find a flight from Seattle to San Francisco on 9 July and book it

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['flights', 'payments']

Failed trace: ['flights', 'payments']

Comparison mode: exact_match
Fields are similar


Comparison field: steps

Successful trace: [{'action': 'search flights', 'app': 'flights'}, {'action': 'book flight', 'app': 'flights'}, {'action': 'charge card', 'app': 'payments'}]

Failed trace: [{'action': 'search flights', 'app': 'flights'}, {'action': 'book flight', 'app': 'flights'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
Fields are similar


Comparison field: steps[].app

Successful trace: ['flights', 'flights', 'payments']

Failed trace: ['flights', 'flights', 'payments']

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['flights.search', 'flights.book', 'payments.charge']

Failed trace: ['flights.search', 'flights.book', 'payments.charge']

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: flights.search

Failed trace: flights.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Responder

**Final divergence: different agents are called for the two traces**


## Comparison 4

### Task: Book a hotel in Austin for 14 to 16 June and add the stay to my calendar.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book a hotel in Austin for 14 to 16 June and add the stay to the calendar

Failed trace: Book a hotel in Austin for 14 to 16 June

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'payments']

Comparison mode: exact_match
**Fields are different**


Comparison field: steps

Successful trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}, {'action': 'add calendar event', 'app': 'calendar'}]

Failed trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
**Fields are different**


Comparison field: steps[].app

Successful trace: ['hotels', 'hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'hotels', 'payments']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: Planner
Different fields: required_apps, steps, steps[].app

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['hotels.search', 'hotels.book', 'payments.charge', 'calendar.add_event']

Failed trace: ['hotels.search', 'hotels.book', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.search

Failed trace: hotels.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.book

Failed trace: hotels.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 5

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: payments.charge

Failed trace: hotels.book

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 6

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: calendar.add_event

Failed trace: payments.charge

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 7

Successful trace: Verifier

Failed trace: Verifier


Comparison field: status

Successful trace: ok

Failed trace: ok

Comparison mode: exact_match
Fields are similar


Comparison field: amount

Successful trace: 356.0

Failed trace: 356.0

Comparison mode: approximate_numeric
Fields are similar


Comparison field: issues

Successful trace: None

Failed trace: None

Comparison mode: field_exists
Fields are similar

**Step outputs are similar**

### Step 8

Successful trace: Responder

Failed trace: Responder


Comparison field: answer

Successful trace: Booked Riverside Lodge in Austin for 14 to 16 June (356.00 USD) and added the stay to your calendar.

Failed trace: Booked Riverside Lodge in Austin for 14 to 16 June, 356.00 USD.

Comparison mode: fuzzy_match
**Fields are different**

**Step outputs are different**

**Both traces completed**


## Comparison 5

### Task: Book a hotel in Austin for 14 to 16 June and add the stay to my calendar.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book a hotel in Austin for 14 to 16 June and add the stay to the calendar

Failed trace: Book a hotel in Austin from 14 to 16 June

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'payments']

Comparison mode: exact_match
**Fields are different**


Comparison field: steps

Successful trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}, {'action': 'add calendar event', 'app': 'calendar'}]

Failed trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
**Fields are different**


Comparison field: steps[].app

Successful trace: ['hotels', 'hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'hotels', 'payments']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: Planner
Different fields: required_apps, steps, steps[].app

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['hotels.search', 'hotels.book', 'payments.charge', 'calendar.add_event']

Failed trace: ['hotels.search', 'hotels.book', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.search

Failed trace: hotels.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.book

Failed trace: hotels.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 5

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: payments.charge

Failed trace: hotels.book

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 6

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: calendar.add_event

Failed trace: payments.charge

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 7

Successful trace: Verifier

Failed trace: Verifier


Comparison field: status

Successful trace: ok

Failed trace: ok

Comparison mode: exact_match
Fields are similar


Comparison field: amount

Successful trace: 356.0

Failed trace: 356.0

Comparison mode: approximate_numeric
Fields are similar


Comparison field: issues

Successful trace: None

Failed trace: None

Comparison mode: field_exists
Fields are similar

**Step outputs are similar**

### Step 8

Successful trace: Responder

Failed trace: Responder


Comparison field: answer

Successful trace: Booked Riverside Lodge in Austin for 14 to 16 June (356.00 USD) and added the stay to your calendar.

Failed trace: Riverside Lodge in Austin is booked for 14 to 16 June at 356.00 USD.

Comparison mode: fuzzy_match
**Fields are different**

**Step outputs are different**

**Both traces completed**


## Comparison 6

### Task: Book a hotel in Austin for 14 to 16 June and add the stay to my calendar.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book an Austin hotel from 14 to 16 June and put the stay in the calendar

Failed trace: Book a hotel in Austin for 14 to 16 June

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'payments']

Comparison mode: exact_match
**Fields are different**


Comparison field: steps

Successful trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}, {'action': 'add calendar event', 'app': 'calendar'}]

Failed trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
**Fields are different**


Comparison field: steps[].app

Successful trace: ['hotels', 'hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'hotels', 'payments']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: Planner
Different fields: required_apps, steps, steps[].app

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['hotels.search', 'hotels.book', 'payments.charge', 'calendar.add_event']

Failed trace: ['hotels.search', 'hotels.book', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.search

Failed trace: hotels.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.book

Failed trace: hotels.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 5

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: payments.charge

Failed trace: hotels.book

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 6

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: calendar.add_event

Failed trace: payments.charge

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 7

Successful trace: Verifier

Failed trace: Verifier


Comparison field: status

Successful trace: ok

Failed trace: ok

Comparison mode: exact_match
Fields are similar


Comparison field: amount

Successful trace: 356.02

Failed trace: 356.0

Comparison mode: approximate_numeric
Fields are similar


Comparison field: issues

Successful trace: None

Failed trace: None

Comparison mode: field_exists
Fields are similar

**Step outputs are similar**

### Step 8

Successful trace: Responder

Failed trace: Responder


Comparison field: answer

Successful trace: Your stay at Riverside Lodge in Austin, 14 to 16 June, is booked for 356.02 USD and is in your calendar.

Failed trace: Booked Riverside Lodge in Austin for 14 to 16 June, 356.00 USD.

Comparison mode: fuzzy_match
**Fields are different**

**Step outputs are different**

**Both traces completed**


## Comparison 7

### Task: Book a hotel in Austin for 14 to 16 June and add the stay to my calendar.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book an Austin hotel from 14 to 16 June and put the stay in the calendar

Failed trace: Book a hotel in Austin from 14 to 16 June

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'payments']

Comparison mode: exact_match
**Fields are different**


Comparison field: steps

Successful trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}, {'action': 'add calendar event', 'app': 'calendar'}]

Failed trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
**Fields are different**


Comparison field: steps[].app

Successful trace: ['hotels', 'hotels', 'payments', 'calendar']

Failed trace: ['hotels', 'hotels', 'payments']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: Planner
Different fields: required_apps, steps, steps[].app

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['hotels.search', 'hotels.book', 'payments.charge', 'calendar.add_event']

Failed trace: ['hotels.search', 'hotels.book', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.search

Failed trace: hotels.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.book

Failed trace: hotels.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 5

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: payments.charge

Failed trace: hotels.book

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 6

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: calendar.add_event

Failed trace: payments.charge

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 7

Successful trace: Verifier

Failed trace: Verifier


Comparison field: status

Successful trace: ok

Failed trace: ok

Comparison mode: exact_match
Fields are similar


Comparison field: amount

Successful trace: 356.02

Failed trace: 356.0

Comparison mode: approximate_numeric
Fields are similar


Comparison field: issues

Successful trace: None

Failed trace: None

Comparison mode: field_exists
Fields are similar

**Step outputs are similar**

### Step 8

Successful trace: Responder

Failed trace: Responder


Comparison field: answer

Successful trace: Your stay at Riverside Lodge in Austin, 14 to 16 June, is booked for 356.02 USD and is in your calendar.

Failed trace: Riverside Lodge in Austin is booked for 14 to 16 June at 356.00 USD.

Comparison mode: fuzzy_match
**Fields are different**

**Step outputs are different**

**Both traces completed**


## Comparison 8

### Task: Book a hotel near the Louvre in Paris for two nights from 12 August.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book a hotel near the Louvre in Paris for two nights from 12 August

Failed trace: Book a hotel close to the Louvre, Paris, two nights from 12 August

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['hotels', 'payments']

Failed trace: ['hotels', 'payments']

Comparison mode: exact_match
Fields are similar


Comparison field: steps

Successful trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}]

Failed trace: [{'action': 'search hotels', 'app': 'hotels'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
Fields are similar


Comparison field: steps[].app

Successful trace: ['hotels', 'hotels', 'payments']

Failed trace: ['hotels', 'hotels', 'payments']

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['hotels.search', 'hotels.book', 'payments.charge']

Failed trace: ['hotels.search', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: ToolSelector
Different fields: selected_tools

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.search

Failed trace: hotels.search

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.book

Failed trace: hotels.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 5

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: payments.charge

Failed trace: payments.charge

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 6

Successful trace: Verifier

Failed trace: Verifier


Comparison field: status

Successful trace: ok

Failed trace: failed

Comparison mode: exact_match
**Fields are different**


Comparison field: amount

Successful trace: 418.0

Failed trace: 418.0

Comparison mode: approximate_numeric
Fields are similar


Comparison field: issues

Successful trace: None

Failed trace: ['payment taken but no reservation exists']

Comparison mode: field_exists
**Fields are different**

**Step outputs are different**

### Step 7

Successful trace: Responder

Failed trace: Responder


Comparison field: answer

Successful trace: Booked Hotel du Palais near the Louvre for 2 nights from 12 August, 418.00 EUR.

Failed trace: Payment of 418.00 EUR went through, but the room is not reserved.

Comparison mode: fuzzy_match
**Fields are different**

**Step outputs are different**

**Both traces completed**


## Comparison 9

### Task: Book a flight to Chicago on 5 October and a hotel there for two nights.

### Step 1

Successful trace: Planner

Failed trace: Planner


Comparison field: intent

Successful trace: Book a flight to Chicago on 5 October and a hotel there for two nights

Failed trace: Book a flight to Chicago on 5 October and a hotel for two nights

Comparison mode: fuzzy_match
Fields are similar


Comparison field: required_apps

Successful trace: ['flights', 'hotels', 'payments']

Failed trace: ['flights', 'payments']

Comparison mode: exact_match
**Fields are different**


Comparison field: steps

Successful trace: [{'action': 'book flight', 'app': 'flights'}, {'action': 'book hotel', 'app': 'hotels'}, {'action': 'charge card', 'app': 'payments'}]

Failed trace: [{'action': 'search flights', 'app': 'flights'}, {'action': 'book flight', 'app': 'flights'}, {'action': 'charge card', 'app': 'payments'}]

Comparison mode: list_length
Fields are similar


Comparison field: steps[].app

Successful trace: ['flights', 'hotels', 'payments']

Failed trace: ['flights', 'flights', 'payments']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

**First divergence between steps is detected**
Agent name: Planner
Different fields: required_apps, steps[].app

### Step 2

Successful trace: ToolSelector

Failed trace: ToolSelector


Comparison field: selected_tools

Successful trace: ['flights.book', 'hotels.book', 'payments.charge']

Failed trace: ['flights.search', 'flights.book', 'payments.charge']

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 3

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: flights.book

Failed trace: flights.search

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 4

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: hotels.book

Failed trace: flights.book

Comparison mode: exact_match
**Fields are different**

**Step outputs are different**

### Step 5

Successful trace: Executor

Failed trace: Executor


Comparison field: tool

Successful trace: payments.charge

Failed trace: payments.charge

Comparison mode: exact_match
Fields are similar

**Step outputs are similar**

### Step 6

Successful trace: Verifier

Failed trace: Verifier


Comparison field: status

Successful trace: ok

Failed trace: ok

Comparison mode: exact_match
Fields are similar


Comparison field: amount

Successful trace: 689.0

Failed trace: 289.0

Comparison mode: approximate_numeric
**Fields are different**


Comparison field: issues

Successful trace: None

Failed trace: None

Comparison mode: field_exists
Fields are similar

**Step outputs are different**

### Step 7

Successful trace: Responder

Failed trace: Responder


Comparison field: answer

Successful trace: Booked AA 2210 to Chicago on 5 October and 2 nights at the Loop Inn, 689.00 USD in total.

Failed trace: Booked AA 2210 to Chicago on 5 October for 289.00 USD.

Comparison mode: fuzzy_match
**Fields are different**

**Step outputs are different**

**Both traces completed**


