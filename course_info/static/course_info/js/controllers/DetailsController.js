// TODO - this is pretty much a copy of the people controller with some mods.
// TODO - this still needs a lot of clean up, we don't need everything in here

(function () {
    var app = angular.module('CourseInfo');
    app.controller('DetailsController', DetailsController);

    function DetailsController($scope, $routeParams, courseInstances, $compile,
                               djangoUrl, $http, $q, $log, $uibModal, $sce) {

        var dc = this;
        dc.courseDetailsUpdateInProgress = false;
        dc.editable = false;

        dc.handleAjaxError = function (data, status, headers, config, statusText) {
            $log.error('Error attempting to ' + config.method + ' ' + config.url +
                ': ' + status + ' ' + statusText + ': ' + JSON.stringify(data));
        };

        dc.setCourseInstance = function (id) {

            var url = djangoUrl.reverse(
                'icommons_rest_api_proxy',
                ['api/course/v2/course_instances/' + id + '/']);
            $http.get(url)
                .success(function (data, status, headers, config, statusText) {
                    //check if the right data was obtained before storing it
                    if (data.course_instance_id == id) {
                        courseInstances.instances[data.course_instance_id] = data;
                        dc.courseInstance = dc.getFormattedCourseInstance(data)
                        // todo: comment
                        // using 354962 for ILE testing
                        var rc = data.course.registrar_code;
                        dc.editable = (rc.startsWith('ILE-')
                                       || rc.startsWith('SB-'));
                        dc.resetForm();
                    } else {
                        $log.error(' CourseInstance record mismatch for id :'
                            + id + ',  fetched record for :' + data.id);
                    }
                })
                .error($scope.handleAjaxError);
        };

        dc.stripQuotes = function(str){
            return str ? str.trim().replace(new RegExp("^\"|\"$", "g"), "") : undefined;
        };

        dc.getFormattedCourseInstance = function (ci) {
            // This is a helper function that formats the CourseInstance metadata
            // and is combination of existing logic in
            // Searchcontroller.courseInstanceToTable and Searchcontroller cell
            // render functions.

            courseInstance = {};
            if (ci) {
                courseInstance['title'] = dc.stripQuotes(ci.title);
                courseInstance['school'] = ci.course ?
                    ci.course.school_id.toUpperCase() : '';
                courseInstance['term'] = ci.term ? ci.term.display_name : '';
                courseInstance['year'] = ci.term ? ci.term.academic_year : '';
                courseInstance['departments'] = ci.course.departments;
                courseInstance['course_groups'] = ci.course.course_groups;
                courseInstance['cid'] = ci.course_instance_id;
                courseInstance['registrar_code_display'] = ci.course ?
                ci.course.registrar_code_display +
                ' (' + ci.course.course_id + ')'.trim() : '';
                courseInstance['description'] = dc.stripQuotes(ci.description);
                courseInstance['short_title'] = dc.stripQuotes(ci.short_title);
                courseInstance['sub_title'] = ci.sub_title;
                courseInstance['meeting_time'] = ci.meeting_time;
                courseInstance['location'] = ci.location;
                courseInstance['instructors_display'] = ci.instructors_display;
                courseInstance['course_instance_id'] = ci.course_instance_id;
                courseInstance['notes'] = dc.stripQuotes(ci.notes);
                courseInstance['conclude_date'] = ci.conclude_date;

                if (ci.secondary_xlist_instances &&
                    ci.secondary_xlist_instances.length > 0) {
                    courseInstance['xlist_status'] = 'Primary';
                } else if (ci.primary_xlist_instances &&
                    ci.primary_xlist_instances.length > 0) {
                    courseInstance['xlist_status'] = 'Secondary';
                } else {
                    courseInstance['xlist_status'] = 'N/A';
                }

                courseInstance['sites'] = ci.sites;
            }
            return courseInstance;
        };

        dc.courseInstanceId = $routeParams.courseInstanceId;

        dc.setCourseInstance($routeParams.courseInstanceId);

        // todo - fix pristine?
        dc.resetForm = function() {
            dc.formDisplayData = angular.copy(dc.courseInstance);
        };

        // todo: data validation
        dc.submitCourseDetailsForm = function() {
            dc.courseDetailsUpdateInProgress = true;
            var postData = {};
            var url = djangoUrl.reverse('icommons_rest_a' +
                'pi_proxy',
                ['api/course/v2/course_instances/'
                + dc.courseInstanceId + '/']);
            var fields = [
                'description',
                'instructors_display',
                'location',
                'meeting_time',
                'notes',
                'short_title',
                'sub_title',
                'title'
            ];
            fields.forEach(function(field) {
                postData[field] = dc.formDisplayData[field];
            });

            // todo: refactor and collapse, no longer need all these functions since they are single-line
            $http.patch(url, postData)
                .then($log, dc.handleAjaxError)
                .finally( function courseDetailsUpdateNoLongerInProgress() {
                    dc.courseDetailsUpdateInProgress = false;
                });
        }
    }
})();
