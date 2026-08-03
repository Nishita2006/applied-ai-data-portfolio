package com.nishita.jobportal.dto;
import jakarta.validation.constraints.Size;
public final class ProfileDtos {
 private ProfileDtos(){}
 public record ProfileRequest(@Size(max=150) String headline,@Size(max=120) String location,@Size(max=2000) String bio,@Size(max=1000) String skills){}
 public record ProfileResponse(String name,String email,String headline,String location,String bio,String skills,String resumeFile){}
 public record CompanyRequest(String name,String website,String location,String description){}
 public record CompanyResponse(Long id,String name,String website,String location,String description){}
}
