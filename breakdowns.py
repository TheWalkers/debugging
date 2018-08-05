
def breakdown_results(breakdown_type, mailing=None, mailings=[], 
                      subject_count=1, variation_count=1):
    # munge and check args
    if mailing:
        mailings.append(mailing)
    _check_breakdown_args(breakdown_type, mailings, subject_count, variation_count)

    # query
    rows = _query(breakdown_type, mailings, int(subject_count or 1), int(variation_count or 1))

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
        
        if len(mailings) < 2:
            raise ValueError("You must compare at least two mailings")

    else:
        raise ValueError("Unknown report type '%s'" % breakdown_type)

