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
    FAIL    ${test_dir:?}/test_pr_0344.md
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
    if [[ "${expected_result}" == "PASS" ]] && [[ "${err:?}" != "0" ]]; then
        echo -e "${cmd:?}"
        ${cmd:?}
        echo -e "FAILURE"
        let "num_failure+=1"
    elif [[ "${expected_result}" == "FAIL" ]] && [[ "${err:?}" == "0" ]]; then
        echo -e "${cmd:?}"
        ${cmd:?}
        echo -e "FAILURE"
        let "num_failure+=1"
    else
        echo -e "SUCCESS"
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


