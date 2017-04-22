import re, sys, os
import json
from urlparse import urlparse
import urllib
import pdb


from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from scrapy.http import Request


from googlescholar.items import *
from misc.log import *
from misc.spider import CommonSpider


reload(sys)
sys.setdefaultencoding('utf8')

def _monkey_patching_HTTPClientParser_statusReceived():
    """
    monkey patching for scrapy.xlib.tx._newclient.HTTPClientParser.statusReceived
    """
    from twisted.web._newclient import HTTPClientParser, ParseError
    old_sr = HTTPClientParser.statusReceived

    def statusReceived(self, status):
        try:
            return old_sr(self, status)
        except ParseError, e:
            if e.args[0] == 'wrong number of parts':
                return old_sr(self, status + ' OK')
            raise
    statusReceived.__doc__ == old_sr.__doc__
    HTTPClientParser.statusReceived = statusReceived


class googlescholarSpider(CommonSpider):
    name = "googlescholar"
    allowed_domains = ["google.com"]
    base_url = 'http://scholar.google.com/scholar?q='
    # __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    # lines = [line.rstrip('\n') for line in open(os.path.join(os.path.dirname(__file__), 'papers.txt'))]
    
    lines = [
        'BPNA Coverage-Based Approach to Recommendation Diversity On Similarity Graph',
        'Ask the GRU: Multi-task Learning for Deep Text Recommendations',
        'Bayesian Low-Rank Determinantal Point Processes',
        'Convolutional Matrix Factorization for Document Context-Aware Recommendation',
        'Crowd-Based Personalized Natural Language Explanations for Recommendations',
        'Deep Neural Networks for YouTube Recommendations',
        'Discovering What Youre Known For: A Contextual Poisson Factorization Approach',
        'Domain-Aware Grade Prediction and Top-n Course Recommendation',
        'Efficient Bayesian Methods for Graph-based Recommendation',
        'Factorization Meets the Item Embedding: Regularizing Matrix Factorization with Item Co-occurrence',
        'Field-aware Factorization Machines for CTR Prediction',
        'Fifty Shades of Ratings: How to Benefit from a Negative Feedback in Top-N Recommendations Tasks',
        'Gaze Prediction for Recommender Systems',
        'Guided Walk: A Scalable Recommendation Algorithm for Complex Heterogeneous Social Networks',
        'Joint User Modeling across Aligned Heterogeneous Sites',
        'Latent Factor Representations for Cold-Start Video Recommendation',
        'Learning Hierarchical Feature Influence for Recommendation by Recursive Regularization',
        'BPNLocal Item-Item Models For Top-N Recommendation',
        'Mechanism Design for Personalized Recommender Systems',
        'Meta-Prod2Vec Product Embeddings Using Side-Information for Recommendation',
        'Mood-Sensitive Truth Discovery For Reliable Recommendation Systems in Social Sensing',
        'Parallel Recurrent Neural Network Architectures for Feature-rich Session-based Recommendations',
        'Personalized Recommendations using Knowledge Graphs: A Probabilistic Logic Programming Approach',
        'Recommending New Items to Ephemeral Groups Using Contextual User Influence',
        'Representation Learning for Homophilic Preferences',
        'STAR: Semiring Trust Inference for Trust-Aware Social Recommenders',
        'BPNTAPER: A Contextual Tensor-Based Approach for Personalized Expert Recommendation',
        'Using Navigation to Improve Recommendations in Real-Time',
        'Vista: A Visually, Socially, and Temporally-aware Model for Artistic Recommendation',
        'Algorithms Aside: Recommendation As The Lens Of Life',
        'Behaviorism is Not Enough',
        'HCI for Recommender Systems: the Past, the Present and the Future',
        'Human-Recommender Systems: From Benchmark Data to Benchmark Cognitive Models',
        'Past, Present, and Future of Recommender Systems: An Industry Perspective',
        'Recommendations with a Purpose',
        'Recommender Systems for Self-Actualization',
        'Recommender Systems with Personality',
        'The Contextual Turn: from Context-Aware to Context-Driven Recommender Systems'
    ]
    start_urls = [ base_url + line for line in lines]
    
    rules = [
        Rule(sle(allow=("scholar\?.*")), callback='parse_1', follow=False),
        Rule(sle(allow=(".*\.pdf"))),
    ]

    def __init__(self, start_url='', *args, **kwargs):
        _monkey_patching_HTTPClientParser_statusReceived()

        if start_url:
            self.start_urls = [start_url]

        
        self.logger.info('{"type":"urls","value": "' + str(self.start_urls) + '"},')
        super(googlescholarSpider, self).__init__(*args, **kwargs)

    #.gs_ri: content besides related html/pdf
    list_css_rules = {
        '.gs_r': {
            'title': '.gs_rt a *::text',
            'url': '.gs_rt a::attr(href)',
            'related-text': '.gs_ggsS::text',
            'related-type': '.gs_ggsS .gs_ctg2::text',
            'related-url': '.gs_ggs a::attr(href)',
            'citation-text': '.gs_fl > a:nth-child(1)::text',
            'citation-url': '.gs_fl > a:nth-child(1)::attr(href)',
            'authors': '.gs_a a::text',
            'description': '.gs_rs *::text',
            'journal-year-src': '.gs_a::text',
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            _monkey_patching_HTTPClientParser_statusReceived()
            yield Request(url, dont_filter=True)

    def save_pdf(self, response):
        path = self.get_path(response.url)
        info(path)
        with open(path, "wb") as f:
            f.write(response.body)

    def parse_1(self, response):
        info('Parse '+response.url)
        #sel = Selector(response)
        #v = sel.css('.gs_ggs a::attr(href)').extract()
        #import pdb; pdb.set_trace()
        x = self.parse_with_rules(response, self.list_css_rules, dict)
        items = []
        if len(x) > 0:
            items = x[0]['.gs_r']
            pp.pprint(items)
        import pdb; pdb.set_trace()
        # return self.parse_with_rules(response, self.css_rules, googlescholarItem)
        for item in items:
            yield item
        # for item in items:
        #     if item['related-url'] == '' or item['related-type'] != '[PDF]':
        #         continue
        #     url = item['related-url']
        #     info('pdf-url: ' + url)
        #     yield Request(url, callback=self.save_pdf)

