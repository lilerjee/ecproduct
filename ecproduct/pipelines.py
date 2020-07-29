# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
#  import os, errno
import pymysql
import datetime
#  import re
#  from ecproduct.items import Product, Market, Attribute, Sku, Image
from pytool.debug import debugger
import collections


class EcproductPipeline(object):
    """
    Process item from product detail page.
    """

    def __init__(self, mysql_host, mysql_username, mysql_password,
                 mysql_database='ecproduct', mysql_charset='utf8'):
        self.mysql_host = mysql_host
        self.mysql_username = mysql_username
        self.mysql_password = mysql_password
        self.mysql_database = mysql_database
        self.mysql_charset = mysql_charset
        self.con = None
        self.cur = None

    def open_spider(self, spider):
        try:
            self.con = pymysql.connect(
                host=self.mysql_host,
                user=self.mysql_username, password=self.mysql_password,
                database=self.mysql_database, charset=self.mysql_charset)
        except pymysql.Error:
            spider.logger.critical(
                'pymysql Error: %s', str(sys.exc_info()[:2]))
            raise

        self.cur = self.con.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.con.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_username=crawler.settings.get('MYSQL_USERNAME'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_database=crawler.settings.get('MYSQL_DATABASE', 'ecproduct'),
            mysql_charset=crawler.settings.get('MYSQL_CHARSET', 'utf8')
        )

    def process_item(self, item, spider):

        # for item_class in [Product, Attribute, Shop, Sku]:
        # for item_class in [Sku]:
        # for item_class in [Product, Attribute]:

        # jd spider debug
        #  spider.logger.info(
        #      '\ncategory_id: %s\ncategory_name: %s\ncategory_status: %s\n'
        #      'category_url: %s' % (len(item['category_id']),
        #                            len(item['category_name']),
        #                            len(item['category_status']),
        #                            len(item['category_url']))
        #  )
        #  spider.logger.info(
        #      '\ncategory_id: %s\ncategory_name: %s\ncategory_status: %s\n'
        #      'category_url: %s' % (len(set(item['category_id'])),
        #                            len(set(item['category_name'])),
        #                            len(set(item['category_status'])),
        #                            len(set(item['category_url'])))
        #  )
        #
        #  repeate_cid = []
        #  for i in set(item['category_id']):
        #      if item['category_id'].count(i) >= 2:
        #          repeate_cid.append(i)
        #  spider.logger.info('repeate_cid=%s' % repeate_cid)

        for item_class in item.__class__.__bases__:
            item_table_name = item_class.__name__.lower()

            #  debugger.print(item_table_name)

            result = self.analyze_item_for_save_sync(
                item, spider,
                item_table_name, item_class)
            debugger.print(result)

            if result['create']:   # for unexisted item in db
                self.save_web_item_into_dst(item, spider, item_table_name,
                                            item_class, result['create'])
            if result['update']:   # for updated item in db
                self.update_dst_item(item, spider, item_table_name,
                                     item_class, result['update'])
            if result['delete']:    # for deleted item in db
                self.delete_dst_item(item, spider, item_table_name,
                                     item_class, result['delete'])

        # print(item)
        return item

    def _get_specific_web_item(self, item, item_class):
        """
        Get specific item fields-values dict whose field have data
        """
        specific_item = {i[0]: i[1] for i in item.items()
                         if i[0] in item_class.fields.keys()}

        return specific_item

    def _get_web_item_combination_list(self, item, spider,
                                       item_class, values_seperator='\n'):
        """
        get all combination of item_name:item_value pairs
        """
        specific_item = self._get_specific_web_item(item, item_class)
        #  dont_update_field_list = self._get_item_special_field_list(
        #      item_class, 'update', False)
        # print('\n', specific_item)
        relationship_key_0 = []
        relationship_key_1 = []
        relationship_key_N = []
        relationship_value_0 = []
        relationship_value_1 = []
        relationship_value_N = []
        for f in specific_item:
            if not item_class.fields.get(f, None):
                relationship_key_0.append(f)
                # print(values_seperator)
                # print(specific_item)
                # print(f)
                relationship_value_0.append(
                    values_seperator.join(specific_item[f]))
                continue
            combination = item_class.fields.get(f).get('combination', None)
            if combination == '1':   # get combination '1'
                relationship_key_1.append(f)
                relationship_value_1.append(specific_item[f])
                # relationship_1.append({f: specific_item[f]})
                continue
            if str(combination).lower() == 'n':   # get combination 'N'
                relationship_key_N.append(f)
                relationship_value_N.append(specific_item[f])
                # relationship_N.append({f: specific_item[f]})
                continue
            # if f in dont_update_field_list:
                # continue
            relationship_key_0.append(f)
            relationship_value_0.append(
                values_seperator.join(specific_item[f]))

        if (len(relationship_key_0) != len(relationship_value_0) or
                len(relationship_key_1) != len(relationship_value_1) or
                len(relationship_key_N) != len(relationship_value_N)):
            spider.logger.error('the length of relationship_key is'
                                'not equal to the one of relationship_value')
            return []

        n_dict = {}
        # debugger.print(relationship_key_1)
        # debugger.print(relationship_value_1)
        if relationship_key_1:
            for num in range(len(relationship_value_1[0])):
                attr_name = []
                for v in relationship_value_1:
                    attr_name.append(v[num])
                # attr_name = relationship_value_1[0][num]
                values_N = []
                for a in relationship_value_N:
                    values_N.append(a[num])
                n_dict[tuple(attr_name)] = values_N
            # print(n_dict)
        else:
            n_dict = dict(zip(relationship_key_0, relationship_value_0))

        # print(relationship_key_1)
        # print(relationship_value_1)
        # print(n_dict)
        n_list = []
        if relationship_key_1:
            for attr in n_dict:
                v = n_dict[attr]
                if v:
                    for a in zip(*v):
                        n_dict1 = {}
                        for (value_id, value) in zip(a, relationship_key_N):
                            # print(value_id, value)
                            n_dict1[value] = value_id
                        for (attr_1_key, attr1_1_value) in zip(
                                relationship_key_1, attr):
                            n_dict1[attr_1_key] = attr1_1_value
                        n_list.append(n_dict1)
                        # print(a)
                else:
                    n_dict1 = {}
                    for (key, value) in zip(relationship_key_1, attr):
                        n_dict1[key] = value
                    n_list.append(n_dict1)

            for com in n_list:
                for (name, value) in zip(relationship_key_0,
                                         relationship_value_0):
                    com[name] = value
        else:
            n_list.append(n_dict)
        # print('\n', n_list)
        return n_list

    def _get_item_special_field_list(self, item_class,
                                     special_field_role, expected_reault):
        field_list = []
        field_dict = item_class.fields
        #  debugger.print(item_class)
        #  debugger.print(special_field_role)
        #  debugger.print(expected_reault)
        for f in field_dict:
            value = field_dict.get(f).get(special_field_role, None)
            if value is expected_reault or value == expected_reault:
                field_list.append(f)
        return field_list

    def _convert_item_value(self, value):
        return str(value) if not isinstance(value, datetime.datetime) else (
            datetime.datetime.strftime(value, '%Y-%m-%d %H:%M:%S'))

    def analyze_item_for_save_sync(self, item, spider, table_name, item_class,
                                   values_seperator='\n'):
        """
        analyze web item and db item.
        get db item data from database, then compaire them
        with one extracted from web, then get the reuslt.
        result: {
                    'create': {'fields':
                        {tuple(primary_key_field_list): web_item_fields_list},
                               'values':
                        create_web_primary_key_value_item_value_dict},
                    'update': {'fields':
                        {tuple(primary_key_field_list):
                            {web_item_fields_list, db_item_fields_list},
                               'values':
                        [update_web_primary_key_value_item_value_dict,
                        update_db_primary_key_value_item_value_dict]},
                    'delete': {'fields':
                        {tuple(primary_key_field_list): db_item_fields_list},
                               'values':
                        delete_db_primary_key_value_item_value_dict},
                    '
                }
        """
        result_dict = {'create': {}, 'update': {}, 'delete': {}}

        status_field_list = self._get_item_special_field_list(
            item_class, 'status', True)
        primary_key_field_list = self._get_item_special_field_list(
            item_class, 'primary_key', True)
        foreign_key_field_list = self._get_item_special_field_list(
            item_class, 'foreign_key', True)
        create_filed_list = self._get_item_special_field_list(
            item_class, 'create', True)
        #  dont_update_field_list = self._get_item_special_field_list(
        #      item_class, 'update', False)
        #  delete_field_list = self._get_item_special_field_list(
        #      item_class, 'update', False)
        debugger.print(primary_key_field_list)

        web_item_combination_list = self._get_web_item_combination_list(
            item, spider, item_class)
        debugger.print(web_item_combination_list)
        if not web_item_combination_list:
            return result_dict

        # don't get the item data from web
        if not (set(primary_key_field_list) < set(
                web_item_combination_list[0].keys())):
            return result_dict

        # get web item primary_value:all_value dict
        web_primary_key_value_item_value_dict = {}
        web_primary_key_value_item_value_dict = {}
        for record in web_item_combination_list:
            web_primary_value_list = []
            web_item_value_list = []
            for f in record:
                web_item_value_list.append(self._convert_item_value(record[f]))
                if f in primary_key_field_list:
                    web_primary_value_list.append(
                        self._convert_item_value(record[f]))
            web_primary_key_value_item_value_dict[
                tuple(web_primary_value_list)] = web_item_value_list

        debugger.print(web_primary_key_value_item_value_dict)

        # one_web_item_combination = web_item_combination_list[0]
        # where_str = ''
        # web_item_fields_list = []
        # primary_key_field_name_list = []
        #  for f in one_web_item_combination:
        #      if f in foreign_key_field_list:
        #          where_str = where_str + (' and ' if where_str else ' '
        #              ) + "%s='%s'" % (f, one_web_item_combination[f])
        #      if f in primary_key_field_list:
        #          primary_key_field_name_list.append(f)
        #      web_item_fields_list.append(f)

        where_dict = collections.defaultdict(list)
        for one_web_item_combination in web_item_combination_list:
            web_item_fields_list = []
            primary_key_field_name_list = []
            for f in one_web_item_combination:
                if f in foreign_key_field_list:
                    where_dict[f].append(one_web_item_combination[f])
                if f in primary_key_field_list:
                    primary_key_field_name_list.append(f)
                web_item_fields_list.append(f)

        where_str = ''
        for f in where_dict:
            # where_str = where_str + (' and ' if where_str else ' '
                    #  ) + "%s in (%s)" % (f,
                    # ','.join("'%s'" % e for e in set(where_dict[f])))
            where_str = (where_str + (' and ' if where_str else ' ') +
                         "%s in (%s)" % (f, ','.join(
                             "'%s'" % self.con.escape_string(str(e))
                             for e in set(where_dict[f]))))

        debugger.print(primary_key_field_name_list)
        # debugger.print(where_str)

        #  for f in status_field_list:
        #      where_str = where_str + (' and ' if where_str else ' '
        #          ) + "%s>='%s'" % (f, '0') # query effective data only

        sql_select_model = "select %s from %s where %s"
        sql_select = sql_select_model % (
            ','.join(web_item_fields_list + status_field_list),
            table_name, where_str)

        try:
            debugger.print(sql_select)
            self.cur.execute(sql_select)
            self.con.commit()
        except Exception:
            spider.logger.error(
                'execute sql_select error: %s' % str(sys.exc_info()[:2]))
            spider.logger.error('sql_select: %s' % sql_select)
            # spider.logger.error('sql_select: %s' % self.cur._last_executed)
            return result_dict

        # print(self.cur.rowcount)
        # cannot find the item in database, then create it
        if self.cur.rowcount <= 0:
            result_dict['create'] = {
                'fields': {tuple(primary_key_field_list):
                           web_item_fields_list},
                'values': web_primary_key_value_item_value_dict}
            # debugger.print(result_dict)
            return result_dict

        # get db item primary_value:all_value dict
        db_primary_key_value_item_value_dict = {}
        for row in self.cur:
            db_primary_value_list = []
            db_primary_db_value_list = []
            for (f, v) in zip(web_item_fields_list + status_field_list, row):
                db_primary_db_value_list.append(self._convert_item_value(v))
                if f in primary_key_field_list:
                    db_primary_value_list.append(self._convert_item_value(v))

            db_primary_key_value_item_value_dict[
                tuple(db_primary_value_list)] = db_primary_db_value_list

        debugger.print(db_primary_key_value_item_value_dict)

        db_keys = db_primary_key_value_item_value_dict.keys()
        web_keys = web_primary_key_value_item_value_dict.keys()

        create_values_dict = {k: web_primary_key_value_item_value_dict[k]
                              for k in web_keys if k not in db_keys}
        if create_values_dict:
            result_dict['create'] = {
                'fields': {tuple(primary_key_field_name_list):
                           web_item_fields_list},
                'values': create_values_dict}

        #  update_values_dict = {k: [web_primary_key_value_item_value_dict[k],
        #                              db_primary_key_value_item_value_dict[k]]
        #                  for k in web_keys if (
        #                       k in db_keys and
        #                       db_primary_key_value_item_value_dict[k][:-2] !=
        #                  web_primary_key_value_item_value_dict[k][:-1])}
        update_values_dict = {
            k: [web_primary_key_value_item_value_dict[k],
                db_primary_key_value_item_value_dict[k]]
            for k in web_keys if (
                k in db_keys and self._compare_item_value(
                    db_primary_key_value_item_value_dict[k],
                    web_primary_key_value_item_value_dict[k],
                    web_item_fields_list,
                    status_field_list + create_filed_list))}
        if update_values_dict:
            result_dict['update'] = {
                'fields': {tuple(primary_key_field_name_list):
                           [web_item_fields_list,
                           web_item_fields_list + status_field_list]},
                'values': update_values_dict}

        delete_values_dict = {k: db_primary_key_value_item_value_dict[k]
                              for k in db_keys if k not in web_keys}
        if delete_values_dict:
            result_dict['delete'] = {
                'fields': {tuple(primary_key_field_name_list):
                           web_item_fields_list + status_field_list},
                'values': delete_values_dict}

        # debugger.print(result_dict)
        return result_dict

    def _compare_item_value(self, db_item_value, web_item_value,
                            web_item_fields_list, dont_compare_field_list):
        for (field, db_value, web_value) in zip(web_item_fields_list,
                                                db_item_value, web_item_value):
            if field in dont_compare_field_list:
                continue
            if db_value != web_value:
                return True
        return False

    def delete_dst_item(self, item, spider, table_name,
                        item_class, processed_item_dict):
        sql_update_model = "update %s set %s where %s"

        status_field_list = self._get_item_special_field_list(
            item_class, 'status', True)
        delete_filed_list = self._get_item_special_field_list(
            item_class, 'delete', True)

        fields = processed_item_dict['fields']
        values = processed_item_dict['values']

        primary_key_name_tuple = ()
        db_item_field_name_list = []
        for k in fields:
            primary_key_name_tuple = k
            db_item_field_name_list = fields[k]

        for key in values:
            db_item_dict = dict(zip(db_item_field_name_list, values[key]))

            # skip the deleted records already
            if status_field_list:
                if str(db_item_dict[status_field_list[0]]) == '-1':
                    continue

            update_value_set_str = ''
            old_value_set_str = ''
            for f in status_field_list:
                update_value_set_str += (
                    (', ' if update_value_set_str else '') +
                    ('%s="%s"' % (f, '-1')))     # '-1' means 'deleted'
                old_value_set_str += ((', ' if old_value_set_str else '') +
                                      ('%s="%s"' % (f, db_item_dict[f])))
            # deleted time
            for f in delete_filed_list:
                update_value_set_str += (
                    (', ' if update_value_set_str else '') +
                    ('%s="%s"' % (f, datetime.datetime.today())))

            where_str = ''
            for (f, v) in zip(primary_key_name_tuple, key):
                where_str += (' and ' if where_str else ' '
                              ) + '%s="%s"' % (f, v)

            sql_update = sql_update_model % (table_name,
                                             update_value_set_str, where_str)

            try:
                debugger.print(sql_update)
                self.cur.execute(sql_update)
                self.con.commit()
                spider.logger.info("delete value - old db value: %s where %s" %
                                   (old_value_set_str, where_str))
                spider.logger.info(sql_update)
            except Exception:
                spider.logger.error('execute sql_update error: %s' %
                                    str(sys.exc_info()[:2]))
                continue

    def save_web_item_into_dst(self, item, spider, table_name,
                               item_class, processed_item_dict):

        # print(require_save_item)

        status_field_list = self._get_item_special_field_list(
            item_class, 'status', True)

        fields = processed_item_dict['fields']
        values = processed_item_dict['values']

        #  primary_key_name_tuple = ()
        web_item_field_name_list = []
        for k in fields:
            #  primary_key_name_tuple = k
            web_item_field_name_list = fields[k]

        save_fields_list = web_item_field_name_list + status_field_list
        values_str_list = []
        values_join = []
        for key in values:
            values_join = values[key]
            for f in status_field_list:
                values_join.append('0')     # '0' is 'created'
            values_str_list.append('(' + ','.join(
                "'%s'" % self.con.escape_string(str(v))
                for v in values_join) + ')')

        sql_save_model = "INSERT INTO %s (%s) VALUES %s"
        sql_save = sql_save_model % (table_name, ','.join(save_fields_list),
                                     ','.join(values_str_list))

        try:
            #  debugger.print(sql_save)
            self.cur.execute(sql_save)
            self.con.commit()
        except Exception:
            spider.logger.error('execute sql_save error: %s' %
                                str(sys.exc_info()[:2]))
            spider.logger.error('sql_save: %s' % sql_save)

    def update_dst_item(self, item, spider, table_name,
                        item_class, processed_item_dict):
        sql_update_model = "update %s set %s where %s"

        status_field_list = self._get_item_special_field_list(
            item_class, 'status', True)
        create_filed_list = self._get_item_special_field_list(
            item_class, 'create', True)

        fields = processed_item_dict['fields']
        values = processed_item_dict['values']

        primary_key_name_tuple = ()
        web_item_field_name_list = []
        db_item_field_name_list = []
        for k in fields:
            primary_key_name_tuple = k
            web_item_field_name_list = fields[k][0]
            db_item_field_name_list = fields[k][1]

        compare_item_field_name_list = [
            n for n in web_item_field_name_list if n not in create_filed_list]

        # find the different values and the according fields
        for key in values:
            web_item_dict = dict(zip(web_item_field_name_list, values[key][0]))
            db_item_dict = dict(zip(db_item_field_name_list, values[key][1]))
            update_value_set_str = ''
            old_value_set_str = ''
            for f in compare_item_field_name_list:
                if web_item_dict[f] != db_item_dict[f]:
                    update_value_set_str += (
                        (', ' if update_value_set_str else '') +
                        ('%s="%s"' % (f, self.con.escape_string(
                            str(web_item_dict[f])))))
                    old_value_set_str += (
                        (', ' if old_value_set_str else '') +
                        ('%s="%s"' % (f, db_item_dict[f])))

            # add field 'status'
            for f in status_field_list:
                update_value_set_str += ', %s="%s"' % (
                    f, int(db_item_dict[f]) + 1)
                old_value_set_str += ', %s="%s"' % (f, db_item_dict[f])
                # recreate the record again after deleting it
                if int(db_item_dict[f]) + 1 == 0:
                    #  create_flag = True
                    for key in create_filed_list:
                        update_value_set_str += ', %s="%s"' % (
                            key, datetime.datetime.today())
                        old_value_set_str += ', %s="%s"' % (
                            key, db_item_dict[f])

            where_str = ''
            for f in primary_key_name_tuple:
                where_str += (' and ' if where_str else ' '
                              ) + '%s="%s"' % (f, db_item_dict[f])

            sql_update = sql_update_model % (
                table_name, update_value_set_str, where_str)

            # debugger.print(update_value_set_str)
            # debugger.print(old_value_set_str)

            try:
                debugger.print(sql_update)
                self.cur.execute(sql_update)
                self.con.commit()
                spider.logger.info("old db value: %s where %s" %
                                   (old_value_set_str, where_str))
                spider.logger.info(sql_update)
            except Exception:
                spider.logger.error('execute sql_update error: %s' %
                                    str(sys.exc_info()[:2]))
                continue
