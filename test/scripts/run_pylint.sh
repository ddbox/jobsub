#!/bin/sh
# pep8 is now called pycodestyle. pep8 is still used in variable names and logging

process_branch() {
    local pylint_log=$1
    local pep8_log=$2
    local results=$3
    local git_branch=$4

    echo "===================================================================="
    echo "GIT BRANCH: $git_branch"
    echo "===================================================================="
    # Initialize logs
    > $pylint_log
    > ${pep8_log}
    > $results

    echo "GIT_BRANCH=\"$git_branch\"" >> $results
    if [ -n "$git_branch" ]; then
        cd $JOBSUB_SRC
        git checkout $git_branch
        checkout_rc=$?
        git pull
        cd $WORKSPACE
        if [ $checkout_rc -ne 0 ]; then
            log_nonzero_rc "git checkout" $?
            echo "GIT_CHECKOUT=\"FAILED\"" >> $results
            return
        fi
    fi
    # Consider success if no git checkout was done
    echo "GIT_CHECKOUT=\"PASSED\"" >> $results

    # pylint related variables
    PYLINT_RCFILE=$WORKSPACE/pylintrc
    PYLINT_OPTIONS=" --rcfile=$PYLINT_RCFILE"



    # pep8 related variables
    # default: E121,E123,E126,E226,E24,E704
    # E501 line too long (90 > 79 characters)
    # E251 unexpected spaces around keyword / parameter equals
    # E303 too many blank lines (2)
    # E225 missing whitespace around operator
    # E231 missing whitespace after ','
    # E228 missing whitespace around modulo operator
    # E302 expected 2 blank lines, found 1
    # E221 multiple spaces before operator
    # E261 at least two spaces before inline comment
    # E111 indentation is not a multiple of four
    # W293 blank line contains whitespace
    # W291 trailing whitespace
    # E265 block comment should start with '# '

    #PEP8_OPTIONS="--ignore=E121,E123,E126,E226,E24,E704,E501,E251,E303,E225,E231,E228,E302,E221,E261,E111,W293,W291,E265"
    
    #uncomment or add lines to taste
    #see tail of pep8.log for counts of
    #various pep8 errors

    PEP8_OPTIONS="--ignore="
    # E111 indentation is not a multiple of four
    PEP8_OPTIONS="$PEP8_OPTIONS""E111"
    # E121 continuation line under-indented for hanging indent
    PEP8_OPTIONS="$PEP8_OPTIONS,E121"
    # E123 closing bracket does not match indentation of opening bracket’s line
    PEP8_OPTIONS="$PEP8_OPTIONS,E123"
    # E126 continuation line over-indented for hanging indent
    PEP8_OPTIONS="$PEP8_OPTIONS,E126"
    # E221 multiple spaces before operator
    PEP8_OPTIONS="$PEP8_OPTIONS,E221"
    # E225 missing whitespace around operator
    PEP8_OPTIONS="$PEP8_OPTIONS,E225"
    # E226 missing whitespace around arithmetic operator
    PEP8_OPTIONS="$PEP8_OPTIONS,E226"
    # E228 missing whitespace around modulo operator
    PEP8_OPTIONS="$PEP8_OPTIONS,E228"
    # E231 missing whitespace after ','
    PEP8_OPTIONS="$PEP8_OPTIONS,E231"
    # E251 unexpected spaces around keyword / parameter equals
    PEP8_OPTIONS="$PEP8_OPTIONS,E251"
    # E261 at least two spaces before inline comment
    PEP8_OPTIONS="$PEP8_OPTIONS,E261"
    # E265 block comment should start with '# '
    PEP8_OPTIONS="$PEP8_OPTIONS,E265"
    # E302 expected 2 blank lines, found 1
    PEP8_OPTIONS="$PEP8_OPTIONS,E302"
    # E303 too many blank lines (3)
    PEP8_OPTIONS="$PEP8_OPTIONS,E303"
    # E402 module level import not at top of file
    PEP8_OPTIONS="$PEP8_OPTIONS,E402"
    # E501 line too long
    PEP8_OPTIONS="$PEP8_OPTIONS,E501"
    # E704 multiple statements on one line (def)
    PEP8_OPTIONS="$PEP8_OPTIONS,E704"
    # W291 trailing whitespace
    PEP8_OPTIONS="$PEP8_OPTIONS,W291"
    # W293 blank line contains whitespace
    PEP8_OPTIONS="$PEP8_OPTIONS,W293"
    # W504 line break after binary operator
    PEP8_OPTIONS="$PEP8_OPTIONS,W504"


    #uncomment to see all pep8 errors
    #PEP8_OPTIONS=""
    
   

    # get list of python scripts 
    cd "${JOBSUB_SRC}"
    export PYTHONPATH=${JOBSUB_SRC}:${JOBSUB_SRC}/server/webapp:${JOBSUB_SRC}/lib/JobsubConfigParser:${JOBSUB_SRC}/lib/logger:${JOBSUB_SRC}/client:$PYTHONPATH
    export PYTHONPATH=${JOBSUB_SRC}/lib/groupsettings:${JOBSUB_SRC}/packaging:$PYTHONPATH
    scripts=`find . -type f   -not -path "*/unarchive/*" -not -path "*/jobsubjobsection/*" -not -path "*/.git/*" -exec file {} \; | grep -i python | cut -d: -f1`
    for script in $scripts; do
      #can't seem to get --ignore or --ignore-modules to work, so do it this way
      PYLINT_SKIP="False"
      for ignore in $PYLINT_IGNORE_LIST; do
          if [ "$ignore" = "$script" ] ; then
             echo "pylint skipping $script" >>  "$pylint_log" 
             PYLINT_SKIP="True"  
          fi
      done
      if [ "$PYLINT_SKIP" != "True" ]; then
          pylint $PYLINT_OPTIONS ${script}  >> $pylint_log || log_nonzero_rc "pylint" $?
      fi
      pycodestyle $PEP8_OPTIONS ${script} >> ${pep8_log} || log_nonzero_rc "pep8" $?
    done

    currdir=`pwd`
    files_checked=`echo $scripts`

    awk '{$1=""; print $0}' ${pep8_log} |  sed -e 's/(.*$//g' | sort | uniq -c | sort -n > ${pep8_log}.sorted
    echo "-------------------" >> ${pep8_log}
    echo "error count summary" >> ${pep8_log}
    echo "-------------------" >> ${pep8_log}
    cat ${pep8_log}.sorted     >> ${pep8_log}
    cd $currdir

    echo "FILES_CHECKED=\"$files_checked\"" >> $results
    echo "FILES_CHECKED_COUNT=`echo $files_checked | wc -w | tr -d " "`" >> $results
    echo "PYLINT_ERROR_FILES_COUNT=`grep '^\*\*\*\*\*\*' $pylint_log | wc -l | tr -d " "`" >> $results
    echo "PYLINT_ERROR_COUNT=`grep '^E:' $pylint_log | wc -l | tr -d " "`" >> $results
    echo "PEP8_ERROR_COUNT=`cat ${pep8_log} | wc -l | tr -d " "`" >> $results
    echo "----------------"
    cat $results
    echo "----------------"

}


init_results_mail () {
    local mail_file=$1
    echo -n > $mail_file
}

init_results_logging() {
    local mail_file=$1
    cat >> $mail_file << TABLE_START
<body>

  <p>
`print_python_info $mail_file`
  </p>
<table style="$HTML_TABLE">
  <thead style="$HTML_THEAD">
    <tr style="$HTML_TR">
      <th style="$HTML_THEAD_TH">GIT BRANCH</th>
      <th style="$HTML_THEAD_TH">FILES CHECKED</th>
      <th style="$HTML_THEAD_TH">FILES WITH ERRORS</th>
      <th style="$HTML_THEAD_TH">TOTAL ERRORS</th>
      <th style="$HTML_THEAD_TH">PEP8 ERRORS</th>
    </tr>
  </thead>
  <tbody>
TABLE_START

}


log_branch_results() {
    local mail_file=$1
    local branch_results=$2
    unset GIT_BRANCH
    unset GIT_CHECKOUT
    unset FILES_CHECKED_COUNT
    unset PYLINT_ERROR_FILES_COUNT
    unset PYLINT_ERROR_COUNT
    unset PEP8_ERROR_COUNT
    source $branch_results

    class=$GIT_CHECKOUT
    if [ "$class" = "PASSED" ]; then
        [ ${PYLINT_ERROR_COUNT:-1} -gt 0 ] && class="FAILED"
    fi
    if [ "$class" = "PASSED" ]; then
        cat >> $mail_file << TABLE_ROW_PASSED
<tr style="$HTML_TR">
    <th style="$HTML_TH">$GIT_BRANCH</th>
    <td style="$HTML_TD_PASSED">${FILES_CHECKED_COUNT:-NA}</td>
    <td style="$HTML_TD_PASSED">${PYLINT_ERROR_FILES_COUNT:-NA}</td>
    <td style="$HTML_TD_PASSED">${PYLINT_ERROR_COUNT:-NA}</td>
    <td style="$HTML_TD_PASSED">${PEP8_ERROR_COUNT:-NA}</td>
</tr>
TABLE_ROW_PASSED
    else
        cat >> $mail_file << TABLE_ROW_FAILED
<tr style="$HTML_TR">
    <th style="$HTML_TH">$GIT_BRANCH</th>
    <td style="$HTML_TD_FAILED">${FILES_CHECKED_COUNT:-NA}</td>
    <td style="$HTML_TD_FAILED">${PYLINT_ERROR_FILES_COUNT:-NA}</td>
    <td style="$HTML_TD_FAILED">${PYLINT_ERROR_COUNT:-NA}</td>
    <td style="$HTML_TD_FAILED">${PEP8_ERROR_COUNT:-NA}</td>
</tr>
TABLE_ROW_FAILED
    fi
}


finalize_results_logging() {
    local mail_file=$1
    cat >> $mail_file << TABLE_END
    </tbody>
</table>
</body>
TABLE_END
}

###############################################################################
# HTML inline CSS
HTML_TABLE="border: 1px solid black;border-collapse: collapse;"
HTML_THEAD="font-weight: bold;border: 0px solid black;background-color: #ffcc00;"
HTML_THEAD_TH="border: 0px solid black;border-collapse: collapse;font-weight: bold;background-color: #ffb300;padding: 8px;"

HTML_TH="border: 0px solid black;border-collapse: collapse;font-weight: bold;background-color: #00ccff;padding: 8px;"
HTML_TR="padding: 5px;text-align: center;"
HTML_TD="border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: center;"

HTML_TR_PASSED="padding: 5px;text-align: center;"
HTML_TD_PASSED="border: 0px solid black;border-collapse: collapse;background-color: #00ff00;padding: 5px;text-align: center;"

HTML_TR_FAILED="padding: 5px;text-align: center;"
HTML_TD_FAILED="border: 0px solid black;border-collapse: collapse;background-color: #ff0000;padding: 5px;text-align: center;"


###############################################################################


git_branches="$@"
shift
WORKSPACE=`pwd`
export JOBSUB_SRC=$WORKSPACE/jobsub
cp $JOBSUB_SRC/test/scripts/pylintrc $WORKSPACE
source $JOBSUB_SRC/test/scripts/utils.sh
if [ "x$VIRTUAL_ENV" = "x" ]; then
    setup_python_venv $WORKSPACE
fi

# Jenkins will reuse the workspace on the slave node if it is available
# There is no reason for not using it, but we need to make sure we keep
# logs for same build together to make it easier to attach to the email
# notifications or for violations. $BUILD_NUMBER is only available when
# running this script from the jenkins environment
LOG_DIR=$WORKSPACE/$BUILD_NUMBER
[ -d $LOG_DIR ] || mkdir -p $LOG_DIR

PYLINT_LOG=$LOG_DIR/pylint.log
PEP8_LOG=$LOG_DIR/pep8.log
RESULTS=$LOG_DIR/results.log
RESULTS_MAIL=$LOG_DIR/mail.results


init_results_mail $RESULTS_MAIL
init_results_logging $RESULTS_MAIL

if [ $# -eq 0 ]; then
    process_branch $PYLINT_LOG $PEP8_LOG $RESULTS $gb
    log_branch_results $RESULTS_MAIL $RESULTS
fi

for gb in `echo $git_branches | sed -e 's/,/ /g'`
do
    if [ -n "$gb" ]; then
        gb_escape=`echo $gb | sed -e 's|/|_|g'`
        pylint_log="$PYLINT_LOG.$gb_escape"
        pep8_log="$PEP8_LOG.$gb_escape"
        results="$RESULTS.$gb_escape"
    fi
    process_branch $pylint_log ${pep8_log} $results $gb
    log_branch_results $RESULTS_MAIL $results
done

finalize_results_logging $RESULTS_MAIL

#mail_results $RESULTS_MAIL "Pylint/PEP8 Validation Results"
