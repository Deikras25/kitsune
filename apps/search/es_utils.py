import elasticutils
import pprint
import pyes

from django.conf import settings


# TODO: Make this less silly.  I do this because if I typo a name,
# pyflakes points it out, but if I typo a string, it doesn't notice
# and typos are always kicking my ass.

TYPE = 'type'
ANALYZER = 'analyzer'
INDEX = 'index'
STORE = 'store'
TERM_VECTOR = 'term_vector'

LONG = 'long'
INTEGER = 'integer'
STRING = 'string'
BOOLEAN = 'boolean'
DATE = 'date'

ANALYZED = 'analyzed'

SNOWBALL = 'snowball'

YES = 'yes'

WITH_POS_OFFSETS = 'with_positions_offsets'


def get_index(model):
    """Returns the index for this model."""
    return (settings.ES_INDEXES.get(model._meta.db_table)
            or settings.ES_INDEXES['default'])


def es_reindex():
    """Reindexes the database in Elastic."""
    es = elasticutils.get_es()

    # Go through and delete, then recreate the indexes.
    for index in settings.ES_INDEXES.values():
        es.delete_index_if_exists(index)

        try:
            es.create_index_if_missing(index)
        except pyes.exceptions.ElasticSearchException:
            # TODO: Why would this throw an exception?  We should handle
            # it.  Maybe Elastic isn't running or something in which case
            # proceeding is an exercise in futility.
            pass

    # Reindex questions.
    import questions.es_search
    questions.es_search.reindex_questions()

    # Reindex wiki documents.
    import wiki.es_search
    wiki.es_search.reindex_documents()

    # Reindex forum posts.
    import forums.es_search
    forums.es_search.reindex_documents()


def es_whazzup():
    """Runs cluster_stats on the Elastic system."""
    import elasticutils
    from forums.models import Post
    from questions.models import Question
    from wiki.models import Document

    es = elasticutils.get_es()

    pprint.pprint(es.cluster_stats())

    print "Totals:"
    print "total questions: ", elasticutils.S(Question).count()
    print "total forum posts: ", elasticutils.S(Post).count()
    print "total wiki docs: ", elasticutils.S(Document).count()
