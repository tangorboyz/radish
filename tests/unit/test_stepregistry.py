# -*- coding: utf-8 -*-

from tests.base import *

from radish.stepregistry import StepRegistry
from radish.exceptions import SameStepError


class StepRegistryTestCase(RadishTestCase):
    """
        Tests for the StepRegistry class
    """
    def test_registering_steps(self):
        """
            Test registering multiple steps
        """
        registry = StepRegistry()
        expect(registry.steps).to.be.empty

        def step_a():
            pass

        def step_b():
            pass

        registry.register("abc", step_a)
        expect(registry.steps).to.have.length_of(1)
        expect(registry.steps["abc"]).to.be.equal(step_a)

        registry.register("def", step_b)
        expect(registry.steps).to.have.length_of(2)
        expect(registry.steps["def"]).to.be.equal(step_b)

    def test_registering_same_step(self):
        """
            Test registering step with same regex
        """
        registry = StepRegistry()
        expect(registry.steps).to.be.empty

        def step_a():
            pass

        def step_b():
            pass

        registry.register("abc", step_a)
        expect(registry.steps).to.have.length_of(1)
        expect(registry.steps["abc"]).to.be.equal(step_a)

        expect(registry.register).when.called_with("abc", step_b).should.throw(SameStepError, "Cannot register step step_b with regex 'abc' because it is already used by step step_a")

        expect(registry.steps).to.have.length_of(1)
        expect(registry.steps["abc"]).to.be.equal(step_a)

    def test_registering_object(self):
        """
            Test registering object as steps
        """
        registry = StepRegistry()
        expect(registry.steps).to.be.empty

        class MySteps(object):
            ignore = ["no_step_method"]

            def some_step(step):
                """When I call some step"""

            def some_other_step(step):
                """
                    Then I expect some behaviour
                """

            def no_step_method(data):
                """
                    This is not a step method
                """

        steps_object = MySteps()
        registry.register_object(steps_object)

        expect(registry.steps).to.have.length_of(2)
        expect(registry.steps["When I call some step"]).to.be.equal(steps_object.some_step)
        expect(registry.steps["Then I expect some behaviour"]).to.be.equal(steps_object.some_other_step)
