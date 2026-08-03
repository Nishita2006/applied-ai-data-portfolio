package com.nishita.jobportal.service;
import com.nishita.jobportal.entity.*;
import com.nishita.jobportal.repository.ApplicationRepository;
import org.springframework.stereotype.Service;
import java.util.*;
@Service public class AnalyticsService{
 private final ApplicationRepository applications; public AnalyticsService(ApplicationRepository a){applications=a;}
 public Map<String,Long> recruiter(Long id){Map<String,Long> m=new LinkedHashMap<>();m.put("totalApplications",applications.countByJobCompanyRecruiterId(id));for(ApplicationStatus s:ApplicationStatus.values())m.put(s.name().toLowerCase(),applications.countByJobCompanyRecruiterIdAndStatus(id,s));return m;}
}
