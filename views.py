from cgi import escape
from breakdowns import breakdown_results

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
  <div>
    <label>
      Mailings (pick at least two):<br />
      <select name="mailings" multiple>
        <option>1 - Here's a pretty cool subject hope y'all open</option>
        <option>2 - This is something completely different</option>
        <option>3 - Huge discounts limited time only</option>
      </select>
    </label>
  </div>
  
  <input type="submit">
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
        <option>1 - Here's a pretty cool subject hope y'all open</option>
        <option>2 - This is something completely different</option>
        <option>3 - Huge discounts limited time only</option>
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
  
  <input type="submit">
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

