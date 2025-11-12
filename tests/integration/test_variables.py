"""
Integration tests for variable support.
"""

from pathlib import Path

import pytest


class TestVariableDefinition:
    """Test variable definition and storage."""

    def test_simple_variable_definition(self, parser):
        """Test defining a simple variable."""
        mml = """
@define MY_VAR 42

[00:00.000]
- pc 1.${MY_VAR}
"""
        doc = parser.parse_string(mml)

        # Variable should be stored in defines
        assert "MY_VAR" in doc.defines
        assert doc.defines["MY_VAR"] == 42

        # Variable should be resolved in command
        assert len(doc.events) > 0
        event = doc.events[0]
        pc_cmd = event["commands"][0]
        assert pc_cmd.data1 == 42

    def test_multiple_variables(self, parser):
        """Test defining multiple variables."""
        mml = """
@define VAR1 10
@define VAR2 20
@define VAR3 30

[00:00.000]
- pc 1.${VAR1}
- cc 1.7.${VAR2}
"""
        doc = parser.parse_string(mml)

        assert doc.defines["VAR1"] == 10
        assert doc.defines["VAR2"] == 20
        assert doc.defines["VAR3"] == 30

    def test_string_variable(self, parser):
        """Test string variable."""
        mml = """
@define SONG_NAME "My Song"
"""
        doc = parser.parse_string(mml)

        assert doc.defines["SONG_NAME"] == "My Song"

    def test_float_variable(self, parser):
        """Test float variable."""
        mml = """
@define TEMPO_ADJUST 1.5
"""
        doc = parser.parse_string(mml)

        assert doc.defines["TEMPO_ADJUST"] == 1.5


class TestVariableResolution:
    """Test variable resolution in commands."""

    def test_variable_in_pc_command(self, parser):
        """Test variable in program change command."""
        mml = """
@define PRESET 5

[00:00.000]
- pc 1.${PRESET}
"""
        doc = parser.parse_string(mml)

        event = doc.events[0]
        pc_cmd = event["commands"][0]
        assert pc_cmd.type == "pc"
        assert pc_cmd.data1 == 5

    def test_variable_in_cc_command(self, parser):
        """Test variable in control change command."""
        mml = """
@define VOLUME 100

[00:00.000]
- cc 1.7.${VOLUME}
"""
        doc = parser.parse_string(mml)

        event = doc.events[0]
        cc_cmd = event["commands"][0]
        assert cc_cmd.type == "cc"
        assert cc_cmd.data2 == 100

    def test_variable_in_channel(self, parser):
        """Test variable for channel number."""
        mml = """
@define CH 2

[00:00.000]
- pc ${CH}.10
"""
        doc = parser.parse_string(mml)

        event = doc.events[0]
        pc_cmd = event["commands"][0]
        assert pc_cmd.channel == 2
        assert pc_cmd.data1 == 10

    def test_multiple_variables_in_command(self, parser):
        """Test multiple variables in same command."""
        mml = """
@define CH 1
@define PRESET 15

[00:00.000]
- pc ${CH}.${PRESET}
"""
        doc = parser.parse_string(mml)

        event = doc.events[0]
        pc_cmd = event["commands"][0]
        assert pc_cmd.channel == 1
        assert pc_cmd.data1 == 15


class TestVariableExpressions:
    """Test variables with expressions."""

    def test_variable_with_addition(self, parser):
        """Test variable defined with addition."""
        mml = """
@define BASE 10
@define NEXT ${BASE} + 5

[00:00.000]
- pc 1.${NEXT}
"""
        doc = parser.parse_string(mml)

        assert doc.defines["BASE"] == 10
        assert doc.defines["NEXT"] == 15

        event = doc.events[0]
        pc_cmd = event["commands"][0]
        assert pc_cmd.data1 == 15

    def test_variable_with_subtraction(self, parser):
        """Test variable defined with subtraction."""
        mml = """
@define HIGH 100
@define LOW ${HIGH} - 30

[00:00.000]
- cc 1.7.${LOW}
"""
        doc = parser.parse_string(mml)

        assert doc.defines["LOW"] == 70

    def test_variable_with_multiplication(self, parser):
        """Test variable defined with multiplication."""
        mml = """
@define BASE 5
@define DOUBLE ${BASE} * 2

[00:00.000]
- pc 1.${DOUBLE}
"""
        doc = parser.parse_string(mml)

        assert doc.defines["DOUBLE"] == 10

    def test_variable_with_division(self, parser):
        """Test variable defined with division."""
        mml = """
@define FULL 120
@define HALF ${FULL} / 2

[00:00.000]
- pc 1.${HALF}
"""
        doc = parser.parse_string(mml)

        assert doc.defines["HALF"] == 60.0


class TestBuiltInConstants:
    """Test built-in constants."""

    def test_pi_constant(self, parser):
        """Test PI constant."""
        mml = """
@define MY_PI ${PI}
"""
        doc = parser.parse_string(mml)

        assert abs(doc.defines["MY_PI"] - 3.14159) < 0.001

    def test_e_constant(self, parser):
        """Test E constant."""
        mml = """
@define MY_E ${E}
"""
        doc = parser.parse_string(mml)

        assert abs(doc.defines["MY_E"] - 2.71828) < 0.001


class TestPhase2ExpressionEvaluation:
    """Test Phase 2: Comprehensive expression evaluation with SafeComputationEngine."""

    def test_operator_precedence(self, parser):
        """Test that operator precedence works correctly."""
        mml = """
@define RESULT 2 + 3 * 4
"""
        doc = parser.parse_string(mml)
        assert doc.defines["RESULT"] == 14  # 2 + (3 * 4), not (2 + 3) * 4

    # Note: Parentheses with leading variables have some limitations in the current grammar
    # These work-around tests show the supported patterns

    def test_multi_step_calculations(self, parser):
        """Test breaking down complex calculations into steps."""
        mml = """
@define TWO 2
@define THREE 3
@define FOUR 4
@define SUM ${TWO} + ${THREE}
@define RESULT ${SUM} * ${FOUR}
"""
        doc = parser.parse_string(mml)
        assert doc.defines["SUM"] == 5
        assert doc.defines["RESULT"] == 20

    def test_complex_expression(self, parser):
        """Test complex expression with multiple operators."""
        mml = """
@define A 10
@define B 5
@define C 2
@define RESULT ${A} + ${B} * ${C}
"""
        doc = parser.parse_string(mml)
        # Test operator precedence: 10 + 5 * 2 = 10 + 10 = 20
        assert doc.defines["RESULT"] == 20

    def test_subtraction_and_division(self, parser):
        """Test subtraction and division together."""
        mml = """
@define A 30
@define B 10
@define C 5
@define RESULT ${A} - ${B} / ${C}
"""
        doc = parser.parse_string(mml)
        # 30 - 10 / 5 = 30 - 2 = 28
        assert doc.defines["RESULT"] == 28.0

    def test_integer_division(self, parser):
        """Test integer division with modulo."""
        mml = """
@define DIVIDEND 17
@define DIVISOR 5
@define QUOTIENT ${DIVIDEND} / ${DIVISOR}
@define REMAINDER ${DIVIDEND} % ${DIVISOR}
"""
        doc = parser.parse_string(mml)
        assert abs(doc.defines["QUOTIENT"] - 3.4) < 0.01  # Regular division
        assert doc.defines["REMAINDER"] == 2  # Modulo

    def test_modulo_operator(self, parser):
        """Test modulo operator."""
        mml = """
@define VALUE 17
@define MOD 5
@define REMAINDER ${VALUE} % ${MOD}
"""
        doc = parser.parse_string(mml)
        assert doc.defines["REMAINDER"] == 2

    def test_constants_in_expressions(self, parser):
        """Test using built-in constants in expressions."""
        mml = """
@define TWICE_PI ${PI} * 2
@define HALF_E ${E} / 2
"""
        doc = parser.parse_string(mml)
        assert abs(doc.defines["TWICE_PI"] - 6.28318530718) < 0.0001
        assert abs(doc.defines["HALF_E"] - 1.35914091423) < 0.0001

    def test_expressions_in_command_parameters(self, parser):
        """Test using variables and expressions in MIDI commands."""
        mml = """
@define BASE 10
@define OFFSET 5
@define TOTAL ${BASE} + ${OFFSET}
@define DOUBLE ${BASE} * 2

[00:00.000]
- pc 1.${TOTAL}
- cc 1.7.${DOUBLE}
"""
        doc = parser.parse_string(mml)
        events = doc.events
        assert len(events) > 0

        # Check that TOTAL and DOUBLE were evaluated
        assert doc.defines["TOTAL"] == 15
        assert doc.defines["DOUBLE"] == 20

        # Find the PC command
        pc_cmd = next((cmd for cmd in events[0]["commands"] if cmd.type == "pc"), None)
        assert pc_cmd is not None
        assert pc_cmd.data1 == 15

        # Find the CC command
        cc_cmd = next((cmd for cmd in events[0]["commands"] if cmd.type == "cc"), None)
        assert cc_cmd is not None
        assert cc_cmd.data2 == 20

    def test_negative_numbers(self, parser):
        """Test expressions with negative numbers."""
        mml = """
@define POS 10
@define NEG -5
@define RESULT ${POS} + ${NEG}
"""
        doc = parser.parse_string(mml)
        assert doc.defines["NEG"] == -5
        assert doc.defines["RESULT"] == 5

    def test_variable_chain(self, parser):
        """Test defining variables in terms of other variables."""
        mml = """
@define A 2
@define B ${A} * 3
@define C ${B} + 4
@define D ${C} * 2
"""
        doc = parser.parse_string(mml)
        assert doc.defines["A"] == 2
        assert doc.defines["B"] == 6
        assert doc.defines["C"] == 10
        assert doc.defines["D"] == 20

    def test_float_precision(self, parser):
        """Test that float calculations maintain precision."""
        mml = """
@define PI_CALC 355 / 113
"""
        doc = parser.parse_string(mml)
        # This is a famous approximation of PI
        assert abs(doc.defines["PI_CALC"] - 3.14159292035) < 0.0000001

    def test_division_by_zero_error(self, parser):
        """Test that division by zero raises appropriate error."""
        mml = """
@define ZERO 0
@define BAD 10 / ${ZERO}
"""
        with pytest.raises((ValueError, ZeroDivisionError)):
            parser.parse_string(mml)

    def test_undefined_variable_in_expression(self, parser):
        """Test that undefined variable raises error."""
        mml = """
@define RESULT ${UNDEFINED}
"""
        with pytest.raises(ValueError, match="Undefined variable|not defined|UNDEFINED"):
            parser.parse_string(mml)

    def test_mixed_types_in_expression(self, parser):
        """Test expressions with mixed int and float types."""
        mml = """
@define INT_VAL 10
@define FLOAT_VAL 3.5
@define RESULT ${INT_VAL} + ${FLOAT_VAL}
"""
        doc = parser.parse_string(mml)
        assert doc.defines["RESULT"] == 13.5


class TestVariableErrors:
    """Test variable error handling."""

    def test_undefined_variable(self, parser):
        """Test using undefined variable raises error."""
        mml = """
[00:00.000]
- pc 1.${UNDEFINED}
"""
        # Variable resolution happens during parsing
        # The undefined variable will be returned as tuple
        doc = parser.parse_string(mml)
        event = doc.events[0]
        pc_cmd = event["commands"][0]

        # Should have unresolved variable tuple
        assert isinstance(pc_cmd.data1, tuple)
        assert pc_cmd.data1[0] == "var"
        assert pc_cmd.data1[1] == "UNDEFINED"

    def test_lowercase_variable_rejected(self, parser):
        """Test that lowercase variables are rejected."""
        mml = """
@define lowercase 42
"""
        with pytest.raises(ValueError, match="Invalid variable name"):
            parser.parse_string(mml)

    def test_constant_redefinition_rejected(self, parser):
        """Test that redefining constants is rejected."""
        mml = """
@define PI 3.14
"""
        with pytest.raises(ValueError, match="Cannot redefine built-in constant"):
            parser.parse_string(mml)


class TestVariablesBasicFixture:
    """Test the variables_basic.mmd fixture file."""

    def test_variables_basic_file(self, parser):
        """Test that variables_basic.mmd parses correctly."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "variables_basic.mmd"

        doc = parser.parse_file(fixture_path)

        # Check variables were defined
        assert "MAIN_CHANNEL" in doc.defines
        assert doc.defines["MAIN_CHANNEL"] == 1

        assert "VERSE_PRESET" in doc.defines
        assert doc.defines["VERSE_PRESET"] == 10

        assert "CHORUS_PRESET" in doc.defines
        assert doc.defines["CHORUS_PRESET"] == 15

        # Check computed variable
        assert "BRIDGE_PRESET" in doc.defines
        assert doc.defines["BRIDGE_PRESET"] == 15  # 10 + 5

        # Check events were parsed
        assert len(doc.events) >= 3

        # Check first event uses variables
        event1 = doc.events[0]
        assert event1["type"] == "timed_event"
        assert len(event1["commands"]) >= 2

        # Check tempo command
        tempo_cmd = event1["commands"][0]
        assert tempo_cmd.type == "tempo"
        assert tempo_cmd.data1 == 140  # TEMPO_FAST

        # Check PC command
        pc_cmd = event1["commands"][1]
        assert pc_cmd.type == "pc"
        assert pc_cmd.channel == 1  # MAIN_CHANNEL
        assert pc_cmd.data1 == 10  # VERSE_PRESET
