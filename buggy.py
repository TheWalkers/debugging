#!/bin/env python2.7
"""
For the debugging question. Assume this is run from a long-running Web 
server process; functions will be called many times.

This file doesn't at all represent our normal code or UI style, but it *is*
supposed to handle even malformed or malicious input without:

    - inaccurate error messages,
    - security vulnerabilities, or
    - crashes

Your task is to look for the bug from the question, but it can't hurt to 
note other places it falls short of that.
"""

from cgi import escape

PAGE_SKEL = """
<!DOCTYPE html>
<html>
  <meta charset="utf-8">
  <head><title>Mailing reports</title></head>
  <body>
    %s
  </body>
</html>
"""
FORMS = """
<h2>Break down results by mailing</h2>
<form action="" method="GET">
  <input type="hidden" name="breakdown_type" value="mailing">
  <label>
    Mailings (pick at least two):
    <select name="mailings" multiple>
      <option>1</option>
      <option>2</option>
      <option>3</option>
    </select>
  </label>
</form>

<h2>Break down results by subject(s)/variation(s)</h2>
<form action="" method="GET">
  <div>
    <label>
      Breakdown type:
      <select name="breakdown_type">
        <option value="subject">Subject line</option>
        <option value="subject_and_variation">Subject line and content variation</option>
      </select>
    </label>
  </div>

  <div>
    <label>
      Mailing:
      <select name="mailing">
        <option>1</option>
        <option>2</option>
        <option>3</option>
      </select>
    </label>
  </div>
  
  <div>
    <label>
      Number of subjects: <input type="text" size="2" name="subject_count"> (if applicable)
    </label>
  </div>
  
  <div>
    <label>
      Number of variations: <input type="text" size="2" name="variation_count"> (if applicable)
    </label>
  </div>
</form>
"""
TBL_HEAD,TBL_FOOT = ("""
<table>
  <thead>
    <tr>
      <th>
        Version<br />
        Click to select as winner
      </th>
      <th>Open rate</th>
      <th>Click rate</th>
      <th>Action rate</th>
    </tr>
  </thead>
  <tbody>
""", """
  </tbody>
</table>
""")

def forms_html(query_string_args):
    return PAGE_SKEL % FORMS

def breakdown_html(query_string_args):
    """
    Return HTML for a mailing breakdown report.

    query_string_args would be formatted {"x": ["1"]} for ?x=1
    """
    
    # filter down to kwargs used by other functions, unwrap lists
    expected_args = ["breakdown_type", "mailing", "mailings", 
                     "subject_count", "variation_count"]
    kwargs = {
        k: v[0] if len(v) else None
        for k, v in query_string_args.items()
        if k in expected_args
    }
    # only handle a list for mailings
    if 'mailings' in query_string_args:
        kwargs['mailings'] = query_string_args['mailings']

    try:
        results = breakdown_results(**kwargs)
    except Exception, e: # show errors
        return PAGE_SKEL % "<h1 style='color:red;'>%s</h1>" % e

    table_html = [TBL_HEAD]
    for row in results:
        link_html = "<a href='%s'>%s</a>" % (
            escape(row['link']), 
            escape(row['name'])
        )
        cells = [link_html]
        cells += [row['opens'], row['clicks'], row['actions']]
        cells_html = '\n'.join(["<td>%s</td>" % val for val in cells])
        table_html.append('<tr>\n%s\n</tr>' % cells_html)

    table_html.append(TBL_FOOT)
    return PAGE_SKEL % '\n'.join(table_html)

def breakdown_results(breakdown_type, mailing=None, mailings=[], 
                      subject_count=1, variation_count=1):
    # munge and check args
    if mailing:
        mailings.append(mailing)
    _check_breakdown_args(breakdown_type, mailings, subject_count, variation_count)

    # query
    rows = _query(breakdown_type, mailings, subject_count, variation_count)

    # add name and link, format varies by report type
    for row in rows:
        if breakdown_type == 'mailing':
            name = "%s (%s)" % (
                row['subject'], 
                row['mailing_id']
            )
            link = '/mailings/%s/' % row['mailing_id']
        elif breakdown_type == 'subject':
            name = row['subject']
            link = '/mailings/%s/?subject_id=%s' % (
                row['mailing_id'], 
                row['subject_id']
            )
        elif breakdown_type == 'subject_and_variation':
            name = '%s variation %s' % (
                row['subject'], 
                row['variation']
            )
            link = '/mailings/%s/?subject_id=%s&variation_id=%s' % (
                row['mailing_id'], 
                row['subject_id'], 
                row['variation_id']
            )
        else:
            raise Exception("Unexpected breakdown_type '%s'" % breakdown_type)

        row['name'], row['link'] = name, link
    
    return rows

def _query(breakdown_type, mailings, subject_count, variation_count):
    """
    Stub where we would really query the DB. Returns fake data here.
    """
    desired_count = len(mailings) * subject_count * variation_count
    return [dict(
        mailing_id=i,
        subject_id=i,
        variation_id=i,
        subject="Subject %d" % i,
        variation="Variation %d" % i,
        opens=i*100,
        clicks=i*10,
        actions=i
    ) for i in range(desired_count)]

def _parses_as_int(v):
    try:
        int(v)
        return True
    except:
        return False

def _check_breakdown_args(breakdown_type, mailings, subject_count, variation_count):
    """
    Check that the user passed in valid 
    """
    if not _parses_as_int(subject_count):
        raise ValueError(
            "Count of subjects provided (%s) is not an integer." 
            % subject_count
        )
    if not _parses_as_int(variation_count):
        raise ValueError(
            "Count of subjects provided (%s) is not an integer." 
            % subject_count
        )

    if breakdown_type in ('subject', 'subject_and_variation'):
        if int(subject_count) < 2 and int(variation_count) < 2:
            raise ValueError(
                "No versions to report on for '%s' report." 
                % breakdown_type
            )

        if len(mailings) != 1:
            raise ValueError(
                "You can only specify one mailing for '%s' reports." 
                % breakdown_type
            )
    
    elif breakdown_type == 'mailing':
        if int(subject_count) != 1 or int(variation_count) != 1:
            raise ValueError(
                "You can only provide one subject or variation for mailing reports."
            )
        
        if not mailings:
            raise ValueError("No mailings specified")

    else:
        raise ValueError("Unknown report type '%s'" % breakdown_type)
