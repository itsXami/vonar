cmake_minimum_required(VERSION 3.22)

project(VOLT VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

if(MSVC)
    # Static runtime: the plugin does not depend on an installed VC++ redistributable.
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()

option(VOLT_BUILD_TOOLS "Build unit tests and the offline preset renderer" ON)

# ---------------------------------------------------------------------------
# JUCE (pinned stable JUCE 8 tag). Override with -DFETCHCONTENT_SOURCE_DIR_JUCE=<path>
# ---------------------------------------------------------------------------
include(FetchContent)
FetchContent_Declare(JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG        8.0.15
    GIT_SHALLOW    TRUE
    GIT_PROGRESS   FALSE)
FetchContent_MakeAvailable(JUCE)

# ---------------------------------------------------------------------------
# Factory presets embedded through BinaryData
# ---------------------------------------------------------------------------
file(GLOB VOLT_PRESET_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/presets/*.json")
list(SORT VOLT_PRESET_FILES)
juce_add_binary_data(VOLT_Presets
    HEADER_NAME VoltPresetData.h
    NAMESPACE   VoltPresetData
    SOURCES     ${VOLT_PRESET_FILES})
set_target_properties(VOLT_Presets PROPERTIES POSITION_INDEPENDENT_CODE ON)

# UI font (Oxanium, SIL Open Font License – see resources/fonts/OFL-Oxanium.txt)
juce_add_binary_data(VOLT_Fonts
    HEADER_NAME VoltFontData.h
    NAMESPACE   VoltFontData
    SOURCES     resources/fonts/Oxanium-Medium.ttf resources/fonts/Oxanium-SemiBold.ttf)
set_target_properties(VOLT_Fonts PROPERTIES POSITION_INDEPENDENT_CODE ON)

# ---------------------------------------------------------------------------
# Core sources shared by the plugin, the tests and the renderer.
# ---------------------------------------------------------------------------
file(GLOB_RECURSE VOLT_CORE_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/Source/*.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/Source/*.h")

add_library(VoltCore INTERFACE)
target_sources(VoltCore INTERFACE ${VOLT_CORE_SOURCES})
target_include_directories(VoltCore INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
target_compile_definitions(VoltCore INTERFACE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    JUCE_DISPLAY_SPLASH_SCREEN=0
    JUCE_USE_FLAC=1
    JUCE_USE_OGGVORBIS=0
    JUCE_SILENCE_XCODE_15_LINKER_WARNING=1
    VOLT_VERSION_STRING="${PROJECT_VERSION}")
target_link_libraries(VoltCore INTERFACE
    VOLT_Presets
    VOLT_Fonts
    juce::juce_audio_utils
    juce::juce_audio_formats
    juce::juce_dsp
    juce::juce_recommended_config_flags
    juce::juce_recommended_warning_flags)

# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------
juce_add_plugin(VOLT
    COMPANY_NAME              "Vonar"
    COMPANY_WEBSITE           "https://github.com/itsXami/vonar"
    BUNDLE_ID                 "com.voltinstruments.volt"
    PLUGIN_MANUFACTURER_CODE  Vltx
    PLUGIN_CODE               Vlt1
    PRODUCT_NAME              "Vonar"
    DESCRIPTION               "Wavetable synthesizer"
    IS_SYNTH                  TRUE
    NEEDS_MIDI_INPUT          TRUE
    NEEDS_MIDI_OUTPUT         FALSE
    IS_MIDI_EFFECT            FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD   FALSE
    VST3_CATEGORIES           Instrument Synth
    FORMATS                   VST3 Standalone)

target_link_libraries(VOLT PRIVATE VoltCore)

# ---------------------------------------------------------------------------
# Tools: unit tests + offline preset renderer (console apps)
# ---------------------------------------------------------------------------
if(VOLT_BUILD_TOOLS)
    juce_add_console_app(VOLT_Tests)
    target_sources(VOLT_Tests PRIVATE tests/TestMain.cpp)
    file(GLOB VOLT_TEST_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tests/*Tests.cpp")
    target_sources(VOLT_Tests PRIVATE ${VOLT_TEST_SOURCES})
    target_compile_definitions(VOLT_Tests PRIVATE VOLT_HEADLESS=1)
    target_link_libraries(VOLT_Tests PRIVATE VoltCore)

    juce_add_console_app(VOLT_Render)
    target_sources(VOLT_Render PRIVATE tools/render/RenderMain.cpp)
    target_compile_definitions(VOLT_Render PRIVATE VOLT_HEADLESS=1)
    target_link_libraries(VOLT_Render PRIVATE VoltCore)

    enable_testing()
    add_test(NAME volt_unit_tests COMMAND VOLT_Tests)
endif()
