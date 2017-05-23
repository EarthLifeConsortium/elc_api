def format_bibjson(pub):

    bibjson = dict()
    other_authors = list()
	
    bibjson.update(type=kind, year=year, title=title)
    bibjson.update(author=[{'name':author1}])
    if author2:
        bibjson['author'].append({'name':author2})
    for next_author in other_authors:
        surname = re.search('[A-Z][a-z]+', next_author)
        fullname = surname.group() + ', ' + \
                   next_author[0:surname.start()-1]
        bibjson['author'].append({'name':fullname})
    bibjson.update(journal=[{'name':journal,'volume':vol,
                             'pages':pages,'editors':editors}])
    bibjson.update(identifier=[{'type':'doi', 'id':doi},
                               {'type':'database', 'id':pub_id}])
