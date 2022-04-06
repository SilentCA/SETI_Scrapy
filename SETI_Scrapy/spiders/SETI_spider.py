import scrapy


class SETI_Spider(scrapy.Spider):
    '''Spider for "setiathome.berkeley.edu".'''
    name = 'SETI'
    USERS_URL = 'https://setiathome.berkeley.edu/show_user.php?userid='
    HOSTS_URL = 'https://setiathome.berkeley.edu/hosts_user.php?sort=rpc_time&rev=0&show_all=1&userid='
    COLUMNS = ['User ID', 'SETI@home member since', 'Country', 'Total credit', 'Recent average credit', 'SETI@home classic workunits', 'SETI@home classic CPU time', 'Operating System', 'Last contact']
    userids = range(1,11)

    def start_requests(self):
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
        yield row
        
