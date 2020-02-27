# -*- coding: utf-8 -*-
import scrapy
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException,StaleElementReferenceException,NoSuchElementException


class PostsSpider(scrapy.Spider):
    name = 'posts'
    allowed_domains = ['www.facebook.com']
    start_urls=["https://facebook.com/"]


    def parse(self,response):
        # valid facebook account's email
        username = ''
        # password of the fb account
        password = ''

        
        # initialize chrome webdriver with optimized mode
        self.driver = webdriver.Chrome("Give the path")
        self.driver.get("https://facebook.com/login/")
        self.logger.info("Sleeping for 3 seconds....")
        sleep(3)
        self.driver.find_element_by_id('email').send_keys(username)
        self.driver.find_element_by_id('pass').send_keys(password+"\n")


        #generating request for filtered url
        self.driver.get('https://www.facebook.com/search/str/election+hacking+united+states/keywords_search?filters_rp_creation_time=%7B%22name%22%3A%22creation_time%22%2C%22args%22%3A%22%7B%5C%22start_year%5C%22%3A%5C%222017%5C%22%2C%5C%22start_month%5C%22%3A%5C%222017-01%5C%22%2C%5C%22end_year%5C%22%3A%5C%222017%5C%22%2C%5C%22end_month%5C%22%3A%5C%222017-12%5C%22%7D%22%7D')


        self.logger.info("Sleeping for 3 seconds....")
        sleep(3)

        #Reading to the all public posts
        self.driver.find_element_by_xpath('//span[@class="_5dw8"]/a').click()
        try:
            self.logger.info("Sleeping for 5 seconds....")
            sleep(5)

            #Scrolling to the end of the page
            try:
                while self.driver.find_element_by_tag_name('div'):



                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    Divs=self.driver.find_element_by_tag_name('div').text
                    if 'End of Results' in Divs:
                        print 'end'
                        break
                    else:
                        continue
            except TypeError:
                self.logger.info("End of the page....")

            self.logger.info("Sleeping for 5 seconds....")
            sleep(5)



            posts_2_expand = self.driver.find_elements_by_xpath('//div[@class="clearfix"]/a[1]')

            # post urls
            posts_uri = self.driver.find_elements_by_xpath('//div[@class="_4rmu"]/div/div[1]/a[1]')

            profileId = []
            p_urls = []


            for i in range(len(posts_2_expand)):
                profileId.append((posts_2_expand[i].get_attribute('data-hovercard').split('id=')[-1]))
                p_urls.append(posts_uri[i].get_attribute('href'))


            # Start clicking at each post
            for post in posts_2_expand:
                post.send_keys("\n")
            self.logger.info("Sleeping for 60 seconds....")
            sleep(60)

            self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)

            #Getting post text

            paras = self.driver.find_elements_by_xpath('//div[starts-with(@class, "_5pbx userContent ")]')
            post_text = []
            try:
                for para in range(len(paras)):
                    post_text.append(paras[para].text.encode('ascii', 'ignore'))
            except TypeError:
                self.logger.info('Text has been scraped.....')


            # Iterate over each profile for remaining data
            for i in range(len(profileId)):
                dic = {}
                self.driver.get("https://facebook.com/"+profileId[i])
                self.logger.info('Sleeping for 2 seconds...')
                sleep(2)

                #To know whether it's page or not
                try:
                    page=self.driver.find_element_by_xpath('//a/span[text()="About"]').text
                except NoSuchElementException:
                    #Logout to login again
                    self.driver.find_element_by_xpath('//div[@id="logoutMenu"]/a').send_keys('\n')
                    self.driver.find_elements_by_xpath('//ul[@class="_54nf"]/li/a[@class="_54nc"]')[-1].send_keys('\n')

                    #again login
                    self.driver.get("https://facebook.com/login/")
                    self.driver.find_element_by_id('email').send_keys(username)
                    self.driver.find_element_by_id('pass').send_keys(password+'\n')

                    self.driver.get("https://facebook.com/" + profileId[i])
                    self.logger.info('Sleeping for 2 seconds...')
                    sleep(2)

                    page = self.driver.find_element_by_xpath('//a/span[text()="About"]').text

                    dic['Post Text'] = post_text[i]
                    dic["Profile ID"] = profileId[i]
                    dic["Profile Url"] = 'https://www.facebook.com/' + profileId[i]
                    dic['Post Url'] = p_urls[i]
                    dic['Went to'] = ''
                    dic['From'] = ''
                    dic['Worked at'] = ''

                    if page:

                        # Under page's about section

                        dic['Name'] = self.driver.find_element_by_xpath('//h1[@id="seo_h1_tag"]/a/span').text

                        about = self.driver.find_elements_by_xpath(
                            '//div[@class="_4-u2 _u9q _3xaf _4-u8"]/div[@class="_2pi9 _2pi2"]')
                        for d in range(len(about)):
                            rawdata = ["Typically replies within a few hours\nSend Message"]
                            if about[d].text in rawdata:
                                dic['Information ' + str(d + 1)] = ''
                            dic['Information ' + str(d + 1)] = about[d].text

                        traffic = self.driver.find_elements_by_xpath(
                            '//div[@class="_2pi9 _2pi2"]/div[@class="clearfix _ikh"]')
                        dic['Like(s)'] = traffic[1].text.replace('people like this', '')

                        dic["Follow"] = traffic[2].text.replace('people follow this', '')

                    else:

                        # Under profile's about section
                        self.driver.find_element_by_xpath('//a[text()="About"]').click()
                        self.logger.info('Sleeping for 3 second...')
                        sleep(3)

                        dic['Name'] = self.driver.find_element_by_xpath('//span[@id="fb-timeline-cover-name"]/a').text

                        try:
                            info = self.driver.find_element_by_xpath('//div[@class="_4ms4"]')
                            all_info = info.text.split('\n')

                            expected_info = ['Worked at', 'Went to', 'From']
                            for y in all_info:
                                for z in expected_info:
                                    if y.startswith(z):
                                        dic[z] = y.split(z)[-1]
                        except NoSuchElementException:
                            yield dic
                            continue

                    yield dic
                    continue

                dic['Post Text'] = post_text[i]
                dic["Profile ID"] = profileId[i]
                dic["Profile Url"] = 'https://www.facebook.com/' + profileId[i]
                dic['Post Url'] = p_urls[i]
                dic['Went to']=''
                dic['From']=''
                dic['Worked at']=''

                if page:

                    #Under page's about section

                    dic['Name']=self.driver.find_element_by_xpath('//h1[@id="seo_h1_tag"]/a/span').text

                    about = self.driver.find_elements_by_xpath('//div[@class="_4-u2 _u9q _3xaf _4-u8"]/div[@class="_2pi9 _2pi2"]')
                    for d in range(len(about)):
                        rawdata=["Typically replies within a few hours\nSend Message" ]
                        if about[d].text in rawdata:
                            dic['Information ' + str(d + 1)] = ''
                        dic['Information '+str(d+1)] = about[d].text


                    traffic=self.driver.find_elements_by_xpath('//div[@class="_2pi9 _2pi2"]/div[@class="clearfix _ikh"]')
                    dic['Like(s)'] = traffic[1].text.replace('people like this','')

                    dic["Follow"]=traffic[2].text.replace('people follow this','')

                else:

                    #Under profile's about section
                    self.driver.find_element_by_xpath('//a[text()="About"]').click()
                    self.logger.info('Sleeping for 3 second...')
                    sleep(3)

                    dic['Name']=self.driver.find_element_by_xpath('//span[@id="fb-timeline-cover-name"]/a').text


                    try:
                        info = self.driver.find_element_by_xpath('//div[@class="_4ms4"]')
                        all_info = info.text.split('\n')

                        expected_info = ['Worked at', 'Went to', 'From']
                        for y in all_info:
                            for z in expected_info:
                                if y.startswith(z):
                                    dic[z]=y.split(z)[-1]
                    except NoSuchElementException:
                        yield dic
                        continue

                yield dic

            self.driver.quit()

        except TimeoutException:
            pass
        
