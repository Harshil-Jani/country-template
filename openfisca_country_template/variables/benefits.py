# -*- coding: utf-8 -*-

# This file defines variables for the modelled legislation.
# A variable is a property of an Entity such as a Person, a Household…
# See https://openfisca.org/doc/key-concepts/variables.html

# Import from openfisca-core the Python objects used to code the legislation in OpenFisca
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_country_template.entities import Household, Person


class basic_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Basic income provided to adults"
    reference = "https://law.gov.example/basic_income"  # Always use the most official source

    # Since Dec 1st 2016, the basic income is provided to any adult, without considering their income.
    def formula_2016_12(person, period, parameters):
        age_condition = person('age', period) >= parameters(period).general.age_of_majority
        return age_condition * parameters(period).benefits.basic_income  # This '*' is a vectorial 'if'. See https://openfisca.org/doc/coding-the-legislation/25_vectorial_computing.html#control-structures

    # From Dec 1st 2015 to Nov 30 2016, the basic income is provided to adults who have no income.
    # Before Dec 1st 2015, the basic income does not exist in the law, and calculating it returns its default value, which is 0.
    def formula_2015_12(person, period, parameters):
        age_condition = person('age', period) >= parameters(period).general.age_of_majority
        salary_condition = person('salary', period) == 0
        return age_condition * salary_condition * parameters(period).benefits.basic_income  # The '*' is also used as a vectorial 'and'. See https://openfisca.org/doc/coding-the-legislation/25_vectorial_computing.html#boolean-operations


class housing_allowance(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Housing allowance"
    reference = "https://law.gov.example/housing_allowance"  # Always use the most official source
    end = '2016-11-30'  # This allowance was removed on the 1st of Dec 2016. Calculating it before this date will always return the variable default value, 0.
    unit = 'currency-EUR'
    documentation = '''
    This allowance was introduced on the 1st of Jan 1980.
    It disappeared in Dec 2016.
    '''

    # This allowance was introduced on the 1st of Jan 1980. Calculating it before this date will always return the variable default value, 0.
    def formula_1980(household, period, parameters):
        '''
        To compute this allowance, the 'rent' value must be provided for the same month, but 'housing_occupancy_status' is not necessary.
        '''
        return household('rent', period) * parameters(period).benefits.housing_allowance


# By default, you can use utf-8 characters in a variable. OpenFisca web API manages utf-8 encoding.
class pension(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Pension for the elderly. Pension attribuée aux personnes âgées. تقاعد."
    reference = [u"https://fr.wikipedia.org/wiki/Retraite_(économie)", u"https://ar.wikipedia.org/wiki/تقاعد"]

    def formula(person, period, parameters):
        '''
        A person's pension depends on their birth date.
        In French: retraite selon l'âge.
        In Arabic: تقاعد.
        '''
        age_condition = person('age', period) >= parameters(period).general.age_of_retirement
        return age_condition


class parenting_allowance(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = ''' Allowance for low income people with children to care for.
                Loosely based on the Australian parenting pension'''
    reference = \
        [u"https://www.servicesaustralia.gov.au/individuals/services/centrelink/parenting-payment/who-can-get-it"]

    def formula(household, period, parameters):
        '''
        A person's parenting allowance depends on how many dependents they have,
        How much they, and their partner, earn
        if they are single with a child under 8
        or if they are partnered with a child under 6.
        '''
        family_income = household('income', period)
        income_threshold = 500
        age_of_youngest_child = household('age_of_youngest_child', period)
        is_single = len(household('parents', period)) == 1
        is_eligible = (is_single and (age_of_youngest_child < 8)) or\
            (age_of_youngest_child < 6) and family_income <= income_threshold
        if is_eligible:
            return parameters(period).benefits.parenting_payment
        else:
            return 0


class household_income(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "The sum of the incomes of those living in a household"

    def formula(household, period, parameters):
        adults = household('parents', period)
        income = 0
        for adult in adults:
            income += adult('salary', period)
        return income


class age_of_youngest_child(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "age of youngest child"

    def formula(household, period, parameters):
        children = household('children', period)
        min_age_in_years = 200  # nobody gets this old!
        for child in children:
            age = child('age', period)
            if age < min_age_in_years:
                min_age_in_years = age
        return age
