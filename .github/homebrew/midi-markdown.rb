# MIDI Markdown Homebrew Formula
# This formula is automatically updated by GitHub Actions on each release
# Manual updates: brew update-python-resources midi-markdown

class MidiMarkdown < Formula
  include Language::Python::Virtualenv

  desc "Human-readable MIDI markup language compiler"
  homepage "https://github.com/cjgdev/midi-markdown"
  url "https://files.pythonhosted.org/packages/source/m/midi-markdown/midi-markdown-0.1.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"
  head "https://github.com/cjgdev/midi-markdown.git", branch: "main"

  depends_on "python@3.12"

  # Main package
  resource "midi-markdown" do
    url "https://files.pythonhosted.org/packages/source/m/midi-markdown/midi-markdown-0.1.0.tar.gz"
    sha256 "PLACEHOLDER_SHA256"
  end

  # Dependencies - run `brew update-python-resources midi-markdown` to regenerate
  resource "mido" do
    url "https://files.pythonhosted.org/packages/source/m/mido/mido-1.3.2.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "python-rtmidi" do
    url "https://files.pythonhosted.org/packages/source/p/python-rtmidi/python-rtmidi-1.5.8.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/source/p/pyyaml/PyYAML-6.0.1.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.12.5.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.8.1.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "lark" do
    url "https://files.pythonhosted.org/packages/source/l/lark/lark-1.3.2.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "prompt-toolkit" do
    url "https://files.pythonhosted.org/packages/source/p/prompt-toolkit/prompt_toolkit-3.0.48.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "readchar" do
    url "https://files.pythonhosted.org/packages/source/r/readchar/readchar-4.2.1.tar.gz"
    sha256 "PLACEHOLDER"
  end

  def install
    virtualenv_install_with_resources

    # Generate shell completions
    generate_completions_from_executable(
      bin/"mmdc",
      shells: [:bash, :zsh, :fish],
      shell_parameter_format: :click
    )

    # Install examples
    pkgshare.install "examples"

    # Install device libraries
    pkgshare.install "devices"
  end

  test do
    # Test version command
    assert_match version.to_s, shell_output("#{bin}/mmdc --version")

    # Test help command
    assert_match "MIDI Markdown Compiler", shell_output("#{bin}/mmdc --help")

    # Test compilation with example file
    example_file = pkgshare/"examples/00_basics/01_hello_world.mmd"
    output_file = testpath/"test.mid"
    system bin/"mmdc", "compile", example_file, "-o", output_file
    assert_predicate output_file, :exist?

    # Test validation
    system bin/"mmdc", "validate", example_file
  end
end
