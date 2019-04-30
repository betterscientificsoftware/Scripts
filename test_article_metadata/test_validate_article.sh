#!/usr/bin/env bash

debug_flag="-V"

metadata_config=config-metadata.txt

color_tty=""
color_tty="--color=tty"

test_dir=test_data

test_articles=(
    FAIL    ${test_dir:?}/test_001_fail.md
    PASS    ${test_dir:?}/test_002_pass.md
    PASS    ${test_dir:?}/test_003_pass.md
    PASS    ${test_dir:?}/test_004_pass.md
    PASS    ${test_dir:?}/test_005_pass.md
    PASS    ${test_dir:?}/test_006_pass.md
    PASS    ${test_dir:?}/test_007_pass.md
    PASS    ${test_dir:?}/test_008_pass.md
    PASS    ${test_dir:?}/test_009_pass.md
    FAIL    ${test_dir:?}/test_010_fail.md
    FAIL    ${test_dir:?}/test_011_fail.md
    FAIL    ${test_dir:?}/test_012_fail.md
    PASS    ${test_dir:?}/test_013_pass_category_development.md
    PASS    ${test_dir:?}/test_014_pass_category_development_deprecated.md
    PASS    ${test_dir:?}/test_015_pass_category_planning.md
    PASS    ${test_dir:?}/test_016_pass_category_planning_deprecated.md
    PASS    ${test_dir:?}/test_017_pass_category_performance.md
    PASS    ${test_dir:?}/test_018_pass_category_performance_deprecated.md    
    PASS    ${test_dir:?}/test_019_pass_category_reliability.md    
    PASS    ${test_dir:?}/test_020_pass_category_collaboration.md    
    PASS    ${test_dir:?}/test_021_pass_category_collaboration_deprecated.md    
    PASS    ${test_dir:?}/test_022_pass_category_skills.md    
    FAIL    ${test_dir:?}/test_pr_0344.md
    PASS    ${test_dir:?}/test_issue-03_01.md
    PASS    ${test_dir:?}/test_issue-03_02.md
    FAIL    ${test_dir:?}/test_issue-03_03.md
)

num_tests=0
num_success=0
num_failure=0

echo ""
for ((i=0; i<${#test_articles[@]}; i+=2)); do
    expected_result=${test_articles[i]}
    filename=${test_articles[i+1]}
    echo -e "Testing: ${expected_result}\t${filename}"
    cmd="python validate_article.py ${debug_flag} -f ${filename} -s ${metadata_config} ${color_tty}"
    let "num_tests+=1"
    ${cmd:?} >& /dev/null
    err=$?
    if [[ "${err:?}" == "0" ]]; then
        echo -e "Actual : PASS"
    else
        echo -e "Actual : FAIL"
    fi
    if [[ "${expected_result}" == "PASS" ]] && [[ "${err:?}" != "0" ]]; then
        echo -e "${cmd:?}"
        ${cmd:?}
        echo -e "Result : FAILURE"
        let "num_failure+=1"
    elif [[ "${expected_result}" == "FAIL" ]] && [[ "${err:?}" == "0" ]]; then
        echo -e "${cmd:?}"
        ${cmd:?}
        echo -e "Result : FAILURE"
        let "num_failure+=1"
    else
        echo -e "Result : SUCCESS"
        let "num_success+=1"
    fi
    echo -e ""
done


echo -e "==============================="
echo -e "  Num Tests  : ${num_tests:?}"
echo -e "  Num SUCCESS: ${num_success:?}"
echo -e "  Num FAILURE: ${num_failure:?}"
echo -e "==============================="

if [[ ${num_failure:?} != 0 ]]; then
    echo -e "Tests failed."
    exit 1
fi


