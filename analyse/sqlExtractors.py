# coding=utf-8
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
# from __future__ import unicode_literals

import sqlparse
from sqlparse.sql import Identifier, IdentifierList, Token
from sqlparse.tokens import Keyword, Name, Whitespace

RESULT_OPERATIONS = {'UNION', 'INTERSECT', 'EXCEPT', 'SELECT', 'RECURSIVE'}
ON_KEYWORD = 'ON'
PRECEDES_TABLE_NAME = {'FROM', 'JOIN', 'DESC', 'DESCRIBE', 'WITH'}


class BaseExtractor(object):
    def __init__(self, sql_statement):
        self.raw = sql_statement
        self.sql = sqlparse.format(sql_statement, reindent=True, keyword_case='upper')
        self._table_names = set()
        self._alias_names = set()
        self._limit = None
        self._parsed = sqlparse.parse(self.stripped())
        for statement in self._parsed:
            self.__extract_from_token(statement)
            self._limit = self._extract_limit_from_query(statement)
        self._table_names = self._table_names - self._alias_names

    @property
    def tables(self):
        return self._table_names

    @property
    def limit(self):
        return self._limit

    def get_type(self):
        return self._parsed[0].get_type()

    def is_select(self):
        return self._parsed[0].get_type() == 'SELECT'

    def is_explain(self):
        return self.stripped().upper().startswith('EXPLAIN')

    def is_with(self):
        for token in self._parsed[0].tokens:
            if token.is_keyword and token.value == 'WITH':
                return True
        return False

    def is_readonly(self):
        return (self.is_select() or self.is_explain() or self.is_with()) and not self.is_into()

    def is_into(self):
        for token in self._parsed[0].tokens:
            if token.is_keyword and token.value == 'INTO':
                return True
        return False

    def stripped(self):
        return self.sql.strip(' \t\n;')

    def get_statements(self):
        statements = []
        for statement in self._parsed:
            if statement:
                sql = str(statement).strip(' \n;\t')
                if sql:
                    statements.append(sql)
        return statements

    @staticmethod
    def __precedes_table_name(token_value):
        for keyword in PRECEDES_TABLE_NAME:
            if keyword in token_value:
                return True
        return False

    @staticmethod
    def get_full_name(identifier):
        if len(identifier.tokens) > 1 and identifier.tokens[1].value == '.':
            return '{}.{}'.format(identifier.tokens[0].value,
                                  identifier.tokens[2].value)
        return identifier.get_real_name()

    @staticmethod
    def __is_result_operation(keyword):
        for operation in RESULT_OPERATIONS:
            if operation in keyword.upper():
                return True
        return False

    @staticmethod
    def __is_identifier(token):
        return isinstance(token, (IdentifierList, Identifier))

    def __process_identifier(self, identifier):
        if '(' not in '{}'.format(identifier):
            self._table_names.add(self.get_full_name(identifier))
            return

        # store aliases
        if hasattr(identifier, 'get_alias'):
            self._alias_names.add(identifier.get_alias())
        if hasattr(identifier, 'tokens'):
            # some aliases are not parsed properly
            if identifier.tokens[0].ttype == Name:
                self._alias_names.add(identifier.tokens[0].value)
        self.__extract_from_token(identifier)

    def as_create_table(self, table_name, overwrite=False):
        exec_sql = ''
        sql = self.stripped()
        if overwrite:
            exec_sql = 'DROP TABLE IF EXISTS {};\n'.format(table_name)
        exec_sql += 'CREATE TABLE {} AS \n{}'.format(table_name, sql)
        return exec_sql

    def __extract_from_token(self, token):
        if not hasattr(token, 'tokens'):
            return

        table_name_preceding_token = False

        for item in token.tokens:
            if item.is_group and not self.__is_identifier(item):
                self.__extract_from_token(item)

            if item.ttype in Keyword:
                if self.__precedes_table_name(item.value.upper()):
                    table_name_preceding_token = True
                    continue

            if not table_name_preceding_token:
                continue

            if item.ttype in Keyword or item.value == ',':
                if (self.__is_result_operation(item.value) or
                        item.value.upper() == ON_KEYWORD):
                    table_name_preceding_token = False
                    continue
                # FROM clause is over
                break

            if isinstance(item, Identifier):
                self.__process_identifier(item)

            if isinstance(item, IdentifierList):
                for token in item.tokens:
                    if self.__is_identifier(token):
                        self.__process_identifier(token)

    def _get_limit_from_token(self, token):
        if token.ttype == sqlparse.tokens.Literal.Number.Integer:
            return int(token.value)
        elif token.is_group:
            return int(token.get_token_at_offset(1).value)

    def _extract_limit_from_query(self, statement):
        limit_token = None
        for pos, item in enumerate(statement.tokens):
            if item.ttype in Keyword and item.value.lower() == 'limit':
                limit_token = statement.tokens[pos + 2]
                return self._get_limit_from_token(limit_token)

    def get_query_with_new_limit(self, new_limit):
        if not self.is_select() or (self.is_select() and self.is_into()):
            return self.sql
        if not self._limit:
            return self.sql + ' LIMIT ' + str(new_limit)
        limit_pos = None
        tokens = self._parsed[0].tokens
        # Add all items to before_str until there is a limit
        for pos, item in enumerate(tokens):
            if item.ttype in Keyword and item.value.lower() == 'limit':
                limit_pos = pos
                break
        limit = tokens[limit_pos + 2]
        if limit.ttype == sqlparse.tokens.Literal.Number.Integer:
            tokens[limit_pos + 2].value = new_limit
        elif limit.is_group:
            tokens[limit_pos + 2].value = (
                '{}, {}'.format(next(limit.get_identifiers()), new_limit)
            )

        str_res = ''
        for i in tokens:
            str_res += str(i.value)
        return str_res


class SqlExtractor(BaseExtractor):
    """提取sql语句"""

    @staticmethod
    def get_full_name(identifier, including_dbs=False):
        if len(identifier.tokens) == 1:
            return identifier.tokens[0].value
        full_tree = ''
        for token in identifier.tokens:
            if token.ttype != Whitespace:
                full_tree += token.value
                break
        return full_tree


class SqlExtractors:
    def __init__(self, sql_list):
        self.__sql_list = sqlparse.split(sql_list, 'utf-8')
        self.__sql_extractors = [SqlExtractor(sql) for sql in self.__sql_list]

    @property
    def extractors(self):
        return self.__sql_extractors


if __name__ == '__main__':
    sql = """
    drop table anqibi;
drop table anqici;
select cm.inserttimeforhis inputDate,
a.policyno,
    trim(c.insuredname) insuredname,c.identifynumber,c.insuredaddress,c.mobile,
    b.licenseno,b.engineno,b.frameno,
    "" xs,"" xtype,
    trim(b.brandname) brandname,a.startdate || " " ||  round(a.starthour,0) || "时--" || a.enddate || " " || round(a.endhour,0) || "时" cistartdate,
    a.sumpremium,1 cicount,
   (select max(policyno) from prpcmain mm join prpcitem_car cc on mm.proposalno = cc.proposalno 
       where mm.riskcode='DAA' and cc.useyears=0 and cc.frameno = b.frameno) policynobi,
  d.thispaytax
from prpcmain a,prpcitem_car b,prpcinsured c,prpccarshiptax d,prpcopymain cm
where a.proposalno = b.proposalno
  and a.proposalno = c.proposalno
  and a.proposalno = d.proposalno
  and a.riskcode="DZA"
  --and a.comcode[1,6]="340217"
  and a.proposalno = cm.applyno
  and cm.inserttimeforhis between ? and ?
  and c.insuredflag[2]='1'
  and a.underwriteflag in ("1","3")
      --安奇送修码3402021000011，伟胜送修码3402015000018
  and b.monopolycode = "3402021000011"
  --and b.licenseno = "皖B53340"
  and b.useyears=?
  into temp anqibi;

  select a.policyno,
  round(nvl((select sum(amount) from prpcitemkind where proposalno = a.proposalno and clausecode='050051' ),null),0) aAmount,
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050051' ),null),2) aPremium,
  
  round(nvl((select sum(amount) from prpcitemkind where proposalno = a.proposalno and clausecode='050052' ),null),0) bAmount,
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050052' ),null),2) bPremium,
  
  round(nvl((select sum(amount) from prpcitemkind where proposalno = a.proposalno and kindcode='050711' ),null),0) b11Amount,
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and kindcode='050711' ),null),2) b11Premium,
  
    round(nvl((select sum(amount) from prpcitemkind where proposalno = a.proposalno and kindcode='050712' ),null),0) b12Amount,
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and kindcode='050712' ),null),2) b12Premium,
  
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050054' ),null),2) gPremium,
  
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050056' ),null),2) fPremium,
  
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050065' ),null),2) q3Premium,
  
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050063' ),null),2) rPremium,
  
  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050060' ),null),2) x1Premium,

  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050057' ),null),2) zPremium,

  round(nvl((select sum(premium) from prpcitemkind where proposalno = a.proposalno and clausecode='050066' ),null),2) mPremium,
  
  a.sumpremium,a.startdate || " " ||  round(a.starthour,0) || "时--" || a.enddate || " " || round(a.endhour,0) || "时" bistartdate

  from prpcmain a
  where a.policyno in (select policynobi from anqibi)
  into temp anqici;
  
  select bi.*,ci.*
  from anqibi bi left join anqici ci on bi.policynobi = ci.policyno
  
"""
    sql_extractors = SqlExtractors(sql)

    # print(sql_extractor.sql)
    # print(sql_extractor.tables)
    for sql in sql_extractors.extractors:
        print('tables: ', list(sql.tables))
        # for token in sql._parsed[0].tokens:
        #     print('token: ',token.ttype, token.value)
