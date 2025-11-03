"""Unit tests for nested alias support (Stage 5).

Tests for aliases calling other aliases with cycle detection and depth limiting.
"""

import pytest

from midi_markdown.alias import (
    AliasMaxDepthError,
    AliasRecursionError,
    AliasResolver,
)


class TestSimpleNesting:
    """Test basic nested alias functionality."""

    def test_simple_two_level_nesting(self, parser):
        """Test alias calling another alias (2 levels deep)."""
        mml = """---
title: Test
---

@alias set_cc {ch} {cc} {val} "Set CC value"
  - cc {ch}.{cc}.{val}
@end

@alias set_routing {ch} {mode} "Set routing mode"
  - set_cc {ch} 85 {mode}
@end

[00:00.000]
- set_routing 2 1
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Resolve the outer alias
        expanded = resolver.resolve("set_routing", [2, 1])

        # Should expand to a single CC command
        assert len(expanded) == 1
        assert expanded[0].type == "control_change"
        assert expanded[0].channel == 2
        assert expanded[0].data1 == 85  # CC number
        assert expanded[0].data2 == 1  # Value

    def test_three_level_nesting(self, parser):
        """Test deep nesting (3 levels)."""
        mml = """---
title: Test
---

@alias base_cc {ch} {cc} {val} "Base CC"
  - cc {ch}.{cc}.{val}
@end

@alias mid_routing {ch} {mode} "Mid level"
  - base_cc {ch} 85 {mode}
@end

@alias top_parallel {ch} "Top level"
  - mid_routing {ch} 1
  - base_cc {ch} 84 64
@end

[00:00.000]
- top_parallel 2
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Resolve top-level alias
        expanded = resolver.resolve("top_parallel", [2])

        # Should expand to 2 CC commands
        assert len(expanded) == 2
        assert all(cmd.type == "control_change" for cmd in expanded)
        assert expanded[0].channel == 2
        assert expanded[0].data1 == 85
        assert expanded[0].data2 == 1
        assert expanded[1].channel == 2
        assert expanded[1].data1 == 84
        assert expanded[1].data2 == 64


class TestCycleDetection:
    """Test circular dependency detection."""

    def test_direct_recursion(self, parser):
        """Test detection of direct recursion (A calls A)."""
        mml = """---
title: Test
---

@alias recursive {ch} "Direct recursion"
  - recursive {ch}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Should raise recursion error
        with pytest.raises(AliasRecursionError) as exc_info:
            resolver.resolve("recursive", [1])

        assert "recursive" in str(exc_info.value)
        assert "Circular alias dependency" in str(exc_info.value)

    def test_indirect_recursion_two_aliases(self, parser):
        """Test detection of indirect recursion (A calls B, B calls A)."""
        mml = """---
title: Test
---

@alias alias_a {ch} "Calls B"
  - alias_b {ch}
@end

@alias alias_b {ch} "Calls A"
  - alias_a {ch}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Should raise recursion error
        with pytest.raises(AliasRecursionError) as exc_info:
            resolver.resolve("alias_a", [1])

        error_msg = str(exc_info.value)
        assert "Circular alias dependency" in error_msg
        # Should show call chain
        assert "alias_a" in error_msg
        assert "alias_b" in error_msg

    def test_indirect_recursion_three_aliases(self, parser):
        """Test detection of longer cycle (A→B→C→A)."""
        mml = """---
title: Test
---

@alias alias_a {ch} "Calls B"
  - alias_b {ch}
@end

@alias alias_b {ch} "Calls C"
  - alias_c {ch}
@end

@alias alias_c {ch} "Calls A - creates cycle"
  - alias_a {ch}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Should raise recursion error
        with pytest.raises(AliasRecursionError) as exc_info:
            resolver.resolve("alias_a", [1])

        error_msg = str(exc_info.value)
        assert "Circular alias dependency" in error_msg


class TestDepthLimiting:
    """Test maximum depth limiting."""

    def test_depth_at_limit_succeeds(self, parser):
        """Test expansion at exactly max_depth succeeds."""
        # Create a chain of 10 aliases (max_depth=10)
        alias_defs = []
        for i in range(1, 11):
            if i < 10:
                alias_defs.append(f'@alias a{i} {{ch}} "Level {i}"\n  - a{i + 1} {{ch}}\n@end\n')
            else:
                alias_defs.append(f'@alias a{i} {{ch}} "Level {i}"\n  - cc {{ch}}.1.0\n@end\n')

        mml = "---\ntitle: Test\n---\n\n" + "\n".join(alias_defs)
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases, max_depth=10)

        # Should succeed - exactly at limit
        expanded = resolver.resolve("a1", [1])
        assert len(expanded) == 1

    def test_depth_exceeds_limit(self, parser):
        """Test expansion beyond max_depth fails."""
        # Create a chain of 11 aliases (max_depth=10)
        alias_defs = []
        for i in range(1, 12):
            if i < 11:
                alias_defs.append(f'@alias a{i} {{ch}} "Level {i}"\n  - a{i + 1} {{ch}}\n@end\n')
            else:
                alias_defs.append(f'@alias a{i} {{ch}} "Level {i}"\n  - cc {{ch}}.1.0\n@end\n')

        mml = "---\ntitle: Test\n---\n\n" + "\n".join(alias_defs)
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases, max_depth=10)

        # Should fail - exceeds limit
        with pytest.raises(AliasMaxDepthError) as exc_info:
            resolver.resolve("a1", [1])

        error_msg = str(exc_info.value)
        assert "maximum depth of 10" in error_msg
        assert "a11" in error_msg  # Should show which alias exceeded

    def test_custom_max_depth(self, parser):
        """Test configurable max_depth."""
        # Chain of 5 aliases
        alias_defs = []
        for i in range(1, 6):
            if i < 5:
                alias_defs.append(f'@alias a{i} {{ch}} "Level {i}"\n  - a{i + 1} {{ch}}\n@end\n')
            else:
                alias_defs.append(f'@alias a{i} {{ch}} "Level {i}"\n  - cc {{ch}}.1.0\n@end\n')

        mml = "---\ntitle: Test\n---\n\n" + "\n".join(alias_defs)
        doc = parser.parse_string(mml)

        # With max_depth=3, should fail
        resolver_low = AliasResolver(doc.aliases, max_depth=3)
        with pytest.raises(AliasMaxDepthError):
            resolver_low.resolve("a1", [1])

        # With max_depth=10, should succeed
        resolver_high = AliasResolver(doc.aliases, max_depth=10)
        expanded = resolver_high.resolve("a1", [1])
        assert len(expanded) == 1


class TestLegitimateRepeatedUse:
    """Test that same alias called multiple times (not recursion) works."""

    def test_repeated_alias_calls_not_recursion(self, parser):
        """Test calling same alias multiple times is not recursion."""
        mml = """---
title: Test
---

@alias set_cc {ch} {cc} {val} "Set CC"
  - cc {ch}.{cc}.{val}
@end

@alias init_device {ch} "Initialize with multiple CCs"
  - set_cc {ch} 1 0
  - set_cc {ch} 2 0
  - set_cc {ch} 3 127
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Should work - same alias called 3 times, but not recursively
        expanded = resolver.resolve("init_device", [1])

        # Should expand to 3 CC commands
        assert len(expanded) == 3
        assert all(cmd.type == "control_change" for cmd in expanded)
        assert expanded[0].data1 == 1
        assert expanded[1].data1 == 2
        assert expanded[2].data1 == 3
