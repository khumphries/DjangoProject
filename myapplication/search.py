# whoosh is a pure python IR library similar to Lucene
# it's used to build search engines; here we do a simple version
# of that. The scoring algorithm used is BM25F

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser

from myapplication.models import Report

def results_as_reports(results):
    reports = []
    for result in results:
        report = Report.objects.filter(shortDescription=result['shortDes'])[0]
        reports.append(report)
    return reports

def get_all_available_reports(request):
    user_group_dict = dict(request.user.groups.values_list(flat=True))
    user_group_list = []
    for value in user_group_dict.values():
        user_group_list.append(value)
    all_reports = Report.objects.filter(report_group__group__in=user_group_list)
    return all_reports

def make_search(queryText, request):
    rgrep = get_all_available_reports(request)
    # both the name and short des are stored; we're currently using short description to find documents (ah),
    # so that's stored too. I'd prefer to store an ID or something, but need to discuss with team
    # long description isn't being stored for space reasons
    schema = Schema(name=TEXT(stored=True), shortDes=TEXT(stored=True), longDes=TEXT)
    inx = create_in("myindex", schema)
    writer = inx.writer()
    for rep in rgrep:
        writer.add_document(name=rep.name, shortDes=rep.shortDescription, longDes=rep.detailedDescription)
    writer.commit()

    with inx.searcher() as searcher:
        parser = MultifieldParser(["name","shortDes","longDes"], schema=schema)
        query = parser.parse(queryText)
        results = searcher.search(query)
        print("search results:")
        print(results)
        return results_as_reports(results)
