# -*- coding: utf-8 -*-

from tests.base import *

from tempfile import NamedTemporaryFile

from radish.parser import FeatureParser
from radish.feature import Feature
from radish.scenario import Scenario
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.exceptions import RadishError, LanguageNotSupportedError


class ParserTestCase(RadishTestCase):
    """
        Tests for the parser class
    """
    def test_language_loading(self):
        """
            Test loading of a specific language
        """
        core = Mock()
        en_feature_parser = FeatureParser(core, "/", 1, language="en")
        expect(en_feature_parser.keywords.feature).to.be.equal("Feature")
        expect(en_feature_parser.keywords.scenario).to.be.equal("Scenario")
        expect(en_feature_parser.keywords.scenario_outline).to.be.equal("Scenario Outline")
        expect(en_feature_parser.keywords.examples).to.be.equal("Examples")

        de_feature_parser = FeatureParser(core, "/", 1, language="de")
        expect(de_feature_parser.keywords.scenario).to.be.equal("Szenario")
        expect(de_feature_parser.keywords.scenario_outline).to.be.equal("Szenario Auslagerung")
        expect(de_feature_parser.keywords.examples).to.be.equal("Beispiele")

        expect(FeatureParser).when.called_with(core, "/", 1, language="foo").should.throw(LanguageNotSupportedError)

    def test_parse_unexisting_featurefile(self):
        """
            Test parsing of an unexisting featurefile
        """
        core = Mock()
        expect(FeatureParser).when.called_with(core, "nonexisting.feature", 1).should.throw(OSError, "Feature file at 'nonexisting.feature' does not exist")

    def test_parse_empty_featurefile(self):
        """
            Test parsing of an empty feature file
        """
        core = Mock()
        with NamedTemporaryFile("w+") as featurefile:
            parser = FeatureParser(core, featurefile.name, 1)
            expect(parser.parse).when.called_with().should.throw(RadishError, "No Feature found in file {0}".format(featurefile.name))

    def test_parse_empty_feature(self):
        """
            Test parsing of an empty feature
        """
        feature = """Feature: some empty feature"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.sentence).to.be.equal("some empty feature")
            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.path).to.be.equal(featurefile.name)
            expect(parser.feature.line).to.be.equal(1)
            expect(parser.feature.scenarios).to.be.empty

    def test_parse_empty_feature_with_description(self):
        """
            Test parsing of an empty feature with desription
        """
        feature = """Feature: some empty feature
    In order to support cool software
    I do fancy BDD testing with radish"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.sentence).to.be.equal("some empty feature")
            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.path).to.be.equal(featurefile.name)
            expect(parser.feature.line).to.be.equal(1)
            expect(parser.feature.scenarios).to.be.empty
            expect(parser.feature.description).to.have.length_of(2)
            expect(parser.feature.description[0]).to.be.equal("In order to support cool software")
            expect(parser.feature.description[1]).to.be.equal("I do fancy BDD testing with radish")

    def test_parse_featurefile_with_multiple_features(self):
        """
            Test parsing a feature file with multiple features
        """
        feature = """Feature: some empty feature
Feature: another empty feature"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            expect(parser.parse).when.called_with().should.throw(RadishError, "radish supports only one Feature per feature file")

    def test_parse_feature_with_empty_scenario(self):
        """
            Test parsing of a feature with one empty scenario
        """
        feature = """Feature: some feature
    Scenario: some empty scenario"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(1)
            expect(parser.feature.scenarios[0].id).to.be.equal(1)
            expect(parser.feature.scenarios[0].sentence).to.be.equal("some empty scenario")
            expect(parser.feature.scenarios[0].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].line).to.be.equal(2)
            expect(parser.feature.scenarios[0].steps).to.be.empty

    def test_parse_feature_with_one_scenario_and_steps(self):
        """
            Test parsing of a feautre with one scenario and multiple steps
        """
        feature = """Feature: some feature
    Scenario: some fancy scenario
        Given I have the number 5
        When I add 2 to my number
        Then I expect my number to be 7 """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(1)
            expect(parser.feature.scenarios).to.have.length_of(1)
            expect(parser.feature.scenarios[0].sentence).to.be.equal("some fancy scenario")

            expect(parser.feature.scenarios[0].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[0].steps[0].id).to.be.equal(1)
            expect(parser.feature.scenarios[0].steps[0].sentence).to.be.equal("Given I have the number 5")
            expect(parser.feature.scenarios[0].steps[0].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[0].line).to.be.equal(3)
            expect(parser.feature.scenarios[0].steps[1].id).to.be.equal(2)
            expect(parser.feature.scenarios[0].steps[1].sentence).to.be.equal("When I add 2 to my number")
            expect(parser.feature.scenarios[0].steps[1].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[1].line).to.be.equal(4)
            expect(parser.feature.scenarios[0].steps[2].id).to.be.equal(3)
            expect(parser.feature.scenarios[0].steps[2].sentence).to.be.equal("Then I expect my number to be 7")
            expect(parser.feature.scenarios[0].steps[2].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[2].line).to.be.equal(5)

    def test_parse_feature_with_multiple_scenarios(self):
        """
            Test parsing of a feature with multiple scenarios and steps
        """
        feature = """Feature: some feature
    Scenario: some fancy scenario
        Given I have the number 5
        When I add 2 to my number
        Then I expect my number to be 7

    Scenario: some other fancy scenario
        Given I have the number 50
        When I add 20 to my number
        Then I expect my number to be 70"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(2)

            expect(parser.feature.scenarios[0].id).to.be.equal(1)
            expect(parser.feature.scenarios[0].sentence).to.be.equal("some fancy scenario")
            expect(parser.feature.scenarios[0].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[0].steps[0].id).to.be.equal(1)
            expect(parser.feature.scenarios[0].steps[0].sentence).to.be.equal("Given I have the number 5")
            expect(parser.feature.scenarios[0].steps[0].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[0].line).to.be.equal(3)
            expect(parser.feature.scenarios[0].steps[1].id).to.be.equal(2)
            expect(parser.feature.scenarios[0].steps[1].sentence).to.be.equal("When I add 2 to my number")
            expect(parser.feature.scenarios[0].steps[1].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[1].line).to.be.equal(4)
            expect(parser.feature.scenarios[0].steps[2].id).to.be.equal(3)
            expect(parser.feature.scenarios[0].steps[2].sentence).to.be.equal("Then I expect my number to be 7")
            expect(parser.feature.scenarios[0].steps[2].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[2].line).to.be.equal(5)

            expect(parser.feature.scenarios[1].id).to.be.equal(2)
            expect(parser.feature.scenarios[1].sentence).to.be.equal("some other fancy scenario")
            expect(parser.feature.scenarios[1].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[1].steps[0].id).to.be.equal(1)
            expect(parser.feature.scenarios[1].steps[0].sentence).to.be.equal("Given I have the number 50")
            expect(parser.feature.scenarios[1].steps[0].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[1].steps[0].line).to.be.equal(8)
            expect(parser.feature.scenarios[1].steps[1].id).to.be.equal(2)
            expect(parser.feature.scenarios[1].steps[1].sentence).to.be.equal("When I add 20 to my number")
            expect(parser.feature.scenarios[1].steps[1].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[1].steps[1].line).to.be.equal(9)
            expect(parser.feature.scenarios[1].steps[2].id).to.be.equal(3)
            expect(parser.feature.scenarios[1].steps[2].sentence).to.be.equal("Then I expect my number to be 70")
            expect(parser.feature.scenarios[1].steps[2].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[1].steps[2].line).to.be.equal(10)

    def test_feature_with_comments(self):
        """
            Test parsing a feature with comments
        """
        feature = """Feature: some feature
    # this is a comment
    Scenario: some fancy scenario
        Given I have the number 5
        When I add 2 to my number
        # this is another comment
        Then I expect my number to be 7

    Scenario: some other fancy scenario
        Given I have the number 50
        # foobar comment
        When I add 20 to my number
        Then I expect my number to be 70
        # another stupid comment"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(2)

            expect(parser.feature.scenarios[0].sentence).to.be.equal("some fancy scenario")
            expect(parser.feature.scenarios[0].line).to.be.equal(3)
            expect(parser.feature.scenarios[0].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[0].steps[0].sentence).to.be.equal("Given I have the number 5")
            expect(parser.feature.scenarios[0].steps[0].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[0].line).to.be.equal(4)
            expect(parser.feature.scenarios[0].steps[1].sentence).to.be.equal("When I add 2 to my number")
            expect(parser.feature.scenarios[0].steps[1].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[1].line).to.be.equal(5)
            expect(parser.feature.scenarios[0].steps[2].sentence).to.be.equal("Then I expect my number to be 7")
            expect(parser.feature.scenarios[0].steps[2].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[0].steps[2].line).to.be.equal(7)

            expect(parser.feature.scenarios[1].sentence).to.be.equal("some other fancy scenario")
            expect(parser.feature.scenarios[1].line).to.be.equal(9)
            expect(parser.feature.scenarios[1].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[1].steps[0].sentence).to.be.equal("Given I have the number 50")
            expect(parser.feature.scenarios[1].steps[0].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[1].steps[0].line).to.be.equal(10)
            expect(parser.feature.scenarios[1].steps[1].sentence).to.be.equal("When I add 20 to my number")
            expect(parser.feature.scenarios[1].steps[1].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[1].steps[1].line).to.be.equal(12)
            expect(parser.feature.scenarios[1].steps[2].sentence).to.be.equal("Then I expect my number to be 70")
            expect(parser.feature.scenarios[1].steps[2].path).to.be.equal(featurefile.name)
            expect(parser.feature.scenarios[1].steps[2].line).to.be.equal(13)

    def test_parse_feature_with_scenario_outline(self):
        """
            Test parsing of a feature file with a scenario outline
        """
        feature = """Feature: some feature
    Scenario Outline: some fancy scenario
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect my number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(1)

            scenario = parser.feature.scenarios[0]
            expect(scenario).to.be.a(ScenarioOutline)
            expect(scenario.id).to.be.equal(1)
            expect(scenario.sentence).to.be.equal("some fancy scenario")

            expect(scenario.steps).to.have.length_of(3)
            expect(scenario.steps[0].id).to.be.equal(1)
            expect(scenario.steps[0].sentence).to.be.equal("Given I have the number <number>")
            expect(scenario.steps[0].path).to.be.equal(featurefile.name)
            expect(scenario.steps[0].line).to.be.equal(3)
            expect(scenario.steps[1].id).to.be.equal(2)
            expect(scenario.steps[1].sentence).to.be.equal("When I add <delta> to my number")
            expect(scenario.steps[1].path).to.be.equal(featurefile.name)
            expect(scenario.steps[1].line).to.be.equal(4)
            expect(scenario.steps[2].id).to.be.equal(3)
            expect(scenario.steps[2].sentence).to.be.equal("Then I expect my number to be <result>")
            expect(scenario.steps[2].path).to.be.equal(featurefile.name)
            expect(scenario.steps[2].line).to.be.equal(5)

            expect(scenario.examples_header).to.be.equal(["number", "delta", "result"])
            expect(scenario.examples).to.have.length_of(3)
            expect(scenario.examples[0].data).to.be.equal(["5", "2", "7"])
            expect(scenario.examples[1].data).to.be.equal(["10", "3", "13"])
            expect(scenario.examples[2].data).to.be.equal(["15", "6", "21"])

            expect(scenario.scenarios).to.have.length_of(3)
            expect(scenario.scenarios[0].id).to.be.equal(2)
            expect(scenario.scenarios[0].steps).to.have.length_of(3)
            expect(scenario.scenarios[0].steps[0].id).to.be.equal(1)
            expect(scenario.scenarios[0].steps[0].sentence).to.be.equal("Given I have the number 5")
            expect(scenario.scenarios[0].steps[1].id).to.be.equal(2)
            expect(scenario.scenarios[0].steps[1].sentence).to.be.equal("When I add 2 to my number")
            expect(scenario.scenarios[0].steps[2].id).to.be.equal(3)
            expect(scenario.scenarios[0].steps[2].sentence).to.be.equal("Then I expect my number to be 7")

            expect(scenario.scenarios[1].id).to.be.equal(3)
            expect(scenario.scenarios[1].steps).to.have.length_of(3)
            expect(scenario.scenarios[0].steps[0].id).to.be.equal(1)
            expect(scenario.scenarios[1].steps[0].sentence).to.be.equal("Given I have the number 10")
            expect(scenario.scenarios[1].steps[1].id).to.be.equal(2)
            expect(scenario.scenarios[1].steps[1].sentence).to.be.equal("When I add 3 to my number")
            expect(scenario.scenarios[1].steps[2].id).to.be.equal(3)
            expect(scenario.scenarios[1].steps[2].sentence).to.be.equal("Then I expect my number to be 13")

            expect(scenario.scenarios[2].id).to.be.equal(4)
            expect(scenario.scenarios[2].steps).to.have.length_of(3)
            expect(scenario.scenarios[2].steps[0].id).to.be.equal(1)
            expect(scenario.scenarios[2].steps[0].sentence).to.be.equal("Given I have the number 15")
            expect(scenario.scenarios[2].steps[1].id).to.be.equal(2)
            expect(scenario.scenarios[2].steps[1].sentence).to.be.equal("When I add 6 to my number")
            expect(scenario.scenarios[2].steps[2].id).to.be.equal(3)
            expect(scenario.scenarios[2].steps[2].sentence).to.be.equal("Then I expect my number to be 21")

    def test_parse_feature_with_scenario_and_scenario_outline(self):
        """
            Test parsing of a feature file with a scenario and a scenario outline
        """
        feature = """Feature: some feature
    Scenario: some normal scenario
        Given I do some stuff
        When I modify it
        Then I expect something else

    Scenario Outline: some fancy scenario
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect my number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |

    Scenario: some other normal scenario
        Given I do some other stuff
        When I modify it
        Then I expect something else
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(3)

            expect(parser.feature.scenarios[0]).to.be.a(Scenario)
            expect(parser.feature.scenarios[0].id).to.be.equal(1)
            expect(parser.feature.scenarios[0].sentence).to.be.equal("some normal scenario")
            expect(parser.feature.scenarios[0].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[0].steps[0].sentence).to.be.equal("Given I do some stuff")
            expect(parser.feature.scenarios[0].steps[1].sentence).to.be.equal("When I modify it")
            expect(parser.feature.scenarios[0].steps[2].sentence).to.be.equal("Then I expect something else")

            expect(parser.feature.scenarios[1]).to.be.a(ScenarioOutline)
            expect(parser.feature.scenarios[1].id).to.be.equal(2)
            expect(parser.feature.scenarios[1].sentence).to.be.equal("some fancy scenario")
            expect(parser.feature.scenarios[1].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[1].steps[0].sentence).to.be.equal("Given I have the number <number>")
            expect(parser.feature.scenarios[1].steps[1].sentence).to.be.equal("When I add <delta> to my number")
            expect(parser.feature.scenarios[1].steps[2].sentence).to.be.equal("Then I expect my number to be <result>")

            expect(parser.feature.scenarios[1].examples_header).to.be.equal(["number", "delta", "result"])
            expect(parser.feature.scenarios[1].examples).to.have.length_of(3)
            expect(parser.feature.scenarios[1].examples[0].data).to.be.equal(["5", "2", "7"])
            expect(parser.feature.scenarios[1].examples[1].data).to.be.equal(["10", "3", "13"])
            expect(parser.feature.scenarios[1].examples[2].data).to.be.equal(["15", "6", "21"])

            expect(parser.feature.scenarios[2]).to.be.a(Scenario)
            expect(parser.feature.scenarios[2].id).to.be.equal(6)
            expect(parser.feature.scenarios[2].sentence).to.be.equal("some other normal scenario")
            expect(parser.feature.scenarios[2].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[2].steps[0].sentence).to.be.equal("Given I do some other stuff")
            expect(parser.feature.scenarios[2].steps[1].sentence).to.be.equal("When I modify it")
            expect(parser.feature.scenarios[2].steps[2].sentence).to.be.equal("Then I expect something else")

    def test_parse_feature_with_scenario_and_examples(self):
        """
            Test parsing of a feature with a scenario which has examples
        """
        feature = """Feature: some feature
    Scenario: some fancy scenario
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect my number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            expect(parser.parse).when.called_with().should.throw(RadishError, "Scenario does not support Examples. Use 'Scenario Outline'")

    def test_parse_steps_with_table(self):
        """
            Test parsing of a feature with a scenario and steps with a table
        """
        feature = """Feature: some feature
    Scenario: some normal scenario
        Given I have the user
            | Bruce     | Wayne      | Batman      |
            | Chuck     | Norris     | PureAwesome |
            | Peter     | Parker     | Spiderman   |
        When I register them in the database
        Then I expect 3 entries in the database
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(1)

            expect(parser.feature.scenarios[0]).to.be.a(Scenario)
            expect(parser.feature.scenarios[0].sentence).to.be.equal("some normal scenario")
            expect(parser.feature.scenarios[0].steps).to.have.length_of(3)
            expect(parser.feature.scenarios[0].steps[0].sentence).to.be.equal("Given I have the user")
            expect(parser.feature.scenarios[0].steps[0].table).to.have.length_of(3)
            expect(parser.feature.scenarios[0].steps[0].table[0]).to.be.equal(["Bruce", "Wayne", "Batman"])
            expect(parser.feature.scenarios[0].steps[0].table[1]).to.be.equal(["Chuck", "Norris", "PureAwesome"])
            expect(parser.feature.scenarios[0].steps[0].table[2]).to.be.equal(["Peter", "Parker", "Spiderman"])

            expect(parser.feature.scenarios[0].steps[1].sentence).to.be.equal("When I register them in the database")
            expect(parser.feature.scenarios[0].steps[1].table).to.have.length_of(0)

            expect(parser.feature.scenarios[0].steps[2].sentence).to.be.equal("Then I expect 3 entries in the database")
            expect(parser.feature.scenarios[0].steps[2].table).to.have.length_of(0)

    def test_detect_scenario_loop(self):
        """
            Test detecting ScenarioLoop on a given line
        """
        line = "Scenario Loop 10: Some fancy scenario loop"

        with NamedTemporaryFile("w+") as featurefile:
            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            result = parser._detect_scenario_loop(line)

            expect(result).to.be.a(tuple)
            expect(result[0]).to.be.equal("Some fancy scenario loop")
            expect(result[1]).to.be.equal(10)

            expect(parser._detect_scenario_loop).when.called_with("").should.return_value(None)
            expect(parser._detect_scenario_loop).when.called_with("Scenario: Some fancy scenario").should.return_value(None)
            expect(parser._detect_scenario_loop).when.called_with("Scenario Outline: Some fancy scenario").should.return_value(None)
            expect(parser._detect_scenario_loop).when.called_with("Scenario Loop: Some fancy scenario").should.return_value(None)
            expect(parser._detect_scenario_loop).when.called_with("Scenario Loop 5.5: Some fancy scenario").should.return_value(None)

    def test_parse_feature_with_scenario_loop(self):
        """
            Test parsing of a feature file with a scenario loop
        """
        feature = """Feature: some feature
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.id).to.be.equal(1)
            expect(parser.feature.sentence).to.be.equal("some feature")
            expect(parser.feature.scenarios).to.have.length_of(1)

            scenario = parser.feature.scenarios[0]
            expect(scenario).to.be.a(ScenarioLoop)
            expect(scenario.id).to.be.equal(1)
            expect(scenario.sentence).to.be.equal("some fancy scenario")

            expect(scenario.steps).to.have.length_of(3)
            expect(scenario.steps[0].id).to.be.equal(1)
            expect(scenario.steps[0].sentence).to.be.equal("Given I have the number 1")
            expect(scenario.steps[0].path).to.be.equal(featurefile.name)
            expect(scenario.steps[0].line).to.be.equal(3)
            expect(scenario.steps[1].id).to.be.equal(2)
            expect(scenario.steps[1].sentence).to.be.equal("When I add 2 to my number")
            expect(scenario.steps[1].path).to.be.equal(featurefile.name)
            expect(scenario.steps[1].line).to.be.equal(4)
            expect(scenario.steps[2].id).to.be.equal(3)
            expect(scenario.steps[2].sentence).to.be.equal("Then I expect my number to be 3")
            expect(scenario.steps[2].path).to.be.equal(featurefile.name)
            expect(scenario.steps[2].line).to.be.equal(5)

            expect(scenario.scenarios).to.have.length_of(10)
            for i in range(10):
                expect(scenario.scenarios[i].id).to.be.equal(i + 2)
                expect(scenario.scenarios[i].steps).to.have.length_of(3)
                expect(scenario.scenarios[i].steps[0].id).to.be.equal(1)
                expect(scenario.scenarios[i].steps[0].sentence).to.be.equal("Given I have the number 1")
                expect(scenario.scenarios[i].steps[1].id).to.be.equal(2)
                expect(scenario.scenarios[i].steps[1].sentence).to.be.equal("When I add 2 to my number")
                expect(scenario.scenarios[i].steps[2].id).to.be.equal(3)
                expect(scenario.scenarios[i].steps[2].sentence).to.be.equal("Then I expect my number to be 3")

    def test_detect_tag(self):
        """
            Test detecting a tag
        """
        feature = """Feature: some feature"""

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            expect(parser._detect_tag).when.called_with("@some_tag").should.return_value(("some_tag", None))
            expect(parser._detect_tag).when.called_with("@some_tag sdfg").should.return_value(("some_tag", None))
            expect(parser._detect_tag).when.called_with("@some_tag_with_arg(args)").should.return_value(("some_tag_with_arg", "args"))
            expect(parser._detect_tag).when.called_with("some_tag").should.return_value(None)
            expect(parser._detect_tag).when.called_with("some_tag sdfg").should.return_value(None)

    def test_parse_feature_with_tag(self):
        """
            Test parsing feature with tag
        """
        feature = """
@some_feature
Feature: some feature
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.tags).to.have.length_of(1)
            expect(parser.feature.tags[0].name).to.be.equal("some_feature")

    def test_parse_feature_with_multiple_tags(self):
        """
            Test parsing feature with tags
        """
        feature = """
@some_feature
@has_scenario_loop
@add_numbers
Feature: some feature
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.tags).to.have.length_of(3)
            expect(parser.feature.tags[0].name).to.be.equal("some_feature")
            expect(parser.feature.tags[1].name).to.be.equal("has_scenario_loop")
            expect(parser.feature.tags[2].name).to.be.equal("add_numbers")

    def test_parse_feature_with_scenario_with_tags(self):
        """
            Test parsing feature with scenario and multiple tags
        """
        feature = """
@some_feature
Feature: some feature
    @some_scenario_loop
    Scenario Loop 10: some fancy scenario
        Given I have the number 1
        When I add 2 to my number
        Then I expect my number to be 3

    Scenario: foo
        When I have a normal scenario
        Then I expect nothing special

    @error_case
    @bad_case
    Scenario: bad case
        Given I have the number 1
        When I add 3 to my number
        Then I expect my number not to be 4
    """

        with NamedTemporaryFile("w+") as featurefile:
            featurefile.write(feature)
            featurefile.flush()

            core = Mock()
            parser = FeatureParser(core, featurefile.name, 1)
            parser.parse()

            expect(parser.feature.tags).to.have.length_of(1)
            expect(parser.feature.tags[0].name).to.be.equal("some_feature")

            expect(parser.feature.scenarios).to.have.length_of(3)

            expect(parser.feature.scenarios[0].tags).to.have.length_of(1)
            expect(parser.feature.scenarios[0].tags[0].name).to.be.equal("some_scenario_loop")

            expect(parser.feature.scenarios[1].tags).to.be.empty

            expect(parser.feature.scenarios[2].tags).to.have.length_of(2)
            expect(parser.feature.scenarios[2].tags[0].name).to.be.equal("error_case")
            expect(parser.feature.scenarios[2].tags[1].name).to.be.equal("bad_case")
