import scrapy
from scrapy.mail import MailSender


class SETI_Spider(scrapy.Spider):
    '''Spider for "setiathome.berkeley.edu".'''
    name = 'SETI'
    USERS_URL = 'https://setiathome.berkeley.edu/show_user.php?userid='
    HOSTS_URL = 'https://setiathome.berkeley.edu/hosts_user.php?sort=rpc_time&rev=0&show_all=1&userid='
    COLUMNS = ['User ID', 'SETI@home member since', 'Country', 'Total credit', 'Recent average credit', 'SETI@home classic workunits', 'SETI@home classic CPU time', 'Operating System', 'Last contact']
    userids = range(1,11)
    total = len(userids)
    smtphost = None
    smtpport = None
    mailfrom = None
    smtpuser = None
    smtppass = None
    mailto = None
    mailer = MailSender(smtphost,mailfrom,smtpuser,smtppass,smtpport,smtpssl=True)

    def __init__(self, stats):
        self.stats = stats
        self.stats.set_value('finished_num', 0)

    @classmethod
    def from_crawler(cls, crawler):
        spider = cls(crawler.stats)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self):
        return self.mailer.send(to=self.mailto,subject='Spider finished',body='Spider finished.')

    def start_requests(self):
        self.logger.info(f"Start spider, total tasks to handle: {len(self.userids)}")
        for id in self.userids:
            yield scrapy.Request(url=self.USERS_URL+str(id))

    def parse(self, response):
        # parse user info table
        keys = response.xpath('/html/body/div/div/table/tr/td[1]/div/table/tr/td[1]/text()')[:-1]
        values =  response.xpath('/html/body/div/div/table/tr/td[1]/div/table/tr/td[2]')
        if len(values):
            # data item
            row = {}.fromkeys(self.COLUMNS)
            for k,v in zip(keys,values):
                if k.get() in self.COLUMNS:
                    row[k.get()] = v.xpath('./text()').get()
            # fetch host info
            yield response.follow(url=self.HOSTS_URL+response.url.split('userid=')[-1], callback=self.parse_host, cb_kwargs={'row':row})
        else:
            self.stats.inc_value('finished_num')
            self.logger.info(f'Task finished {self.stats.get_value("finished_num")}/{self.total}')
            yield None

    def parse_host(self, response, row):
        latest_date = response.xpath('/html/body/div/div/table/tr[2]/td[9]/text()').get()
        if latest_date:  # if host info table not empty
            if 'Microsoft' in response.text:
                if 'Linux' in response.text:
                    os = 'Both'
                else:
                    os = 'Ms Windows'
            else:
                if 'Linux' in response.text:
                    os = 'Linux'
                else:
                    os = 'Other'
            row['Operating System'] = os
            row['Last contact'] = latest_date
        self.stats.inc_value('finished_num')
        self.logger.info(f'Task finished {self.stats.get_value("finished_num")}/{self.total}')
        yield row
        
